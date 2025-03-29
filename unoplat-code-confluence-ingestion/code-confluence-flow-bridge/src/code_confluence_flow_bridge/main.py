from src.code_confluence_flow_bridge.db import create_db_and_tables, get_session
from src.code_confluence_flow_bridge.logging.log_config import setup_logging
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings, RepositorySettings
from src.code_confluence_flow_bridge.models.credentials import Credentials
from src.code_confluence_flow_bridge.models.github.github_repo import GitHubLicense, GitHubOwner, GitHubRepo, GitHubRepoSummary
from src.code_confluence_flow_bridge.processor.codebase_child_workflow import CodebaseChildWorkflow
from src.code_confluence_flow_bridge.processor.codebase_processing.codebase_processing_activity import CodebaseProcessingActivity
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import ConfluenceGitGraph
from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import PackageManagerMetadataIngestion
from src.code_confluence_flow_bridge.processor.repo_workflow import RepoWorkflow

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.concurrency import asynccontextmanager
from loguru import logger
from temporalio.client import Client, WorkflowHandle
from temporalio.worker import Worker

# Setup logging
logger = setup_logging()


async def get_temporal_client() -> Client:
    """Create and return a Temporal client instance."""
    # Connect to local temporal server
    # Read from env - TEMPORAL_SERVER_ADDRESS, default to localhost:7233
    temporal_server = os.getenv("TEMPORAL_SERVER_ADDRESS", "localhost:7233")
    temporal_client = await Client.connect(temporal_server)
    return temporal_client


async def run_worker(activities: List[Callable], client: Client, activity_executor: ThreadPoolExecutor) -> None:
    """
    Run the Temporal worker with given activities

    Args:
        activities: List of activity functions
        client: Temporal client
        activity_executor: Thread pool executor for activities
    """
    worker = Worker(client, task_queue="unoplat-code-confluence-repository-context-ingestion", workflows=[RepoWorkflow, CodebaseChildWorkflow], activities=activities, activity_executor=activity_executor)

    await worker.run()


async def start_workflow(temporal_client: Client, repository: RepositorySettings, github_token: str):
    workflow_handle = await temporal_client.start_workflow(RepoWorkflow.run, args=(repository, github_token), id=repository.git_url, task_queue="unoplat-code-confluence-repository-context-ingestion")
    logger.info(f"Started workflow. Workflow ID: {workflow_handle.id}, RunID {workflow_handle.result_run_id}")
    return workflow_handle


# Create FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.code_confluence_env = EnvironmentSettings()
    app.state.temporal_client = await get_temporal_client()
    app.state.code_confluence_graph_ingestion = CodeConfluenceGraphIngestion(code_confluence_env=app.state.code_confluence_env)
    await app.state.code_confluence_graph_ingestion.initialize()

    app.state.activity_executor = ThreadPoolExecutor()

    # Define activities
    activities: List[Callable] = []
    git_activity = GitActivity()
    activities.append(git_activity.process_git_activity)

    package_metadata_activity = PackageMetadataActivity()
    activities.append(package_metadata_activity.get_package_metadata)

    confluence_git_graph = ConfluenceGitGraph(code_confluence_graph_ingestion=app.state.code_confluence_graph_ingestion)
    activities.append(confluence_git_graph.insert_git_repo_into_graph_db)

    codebase_package_ingestion = PackageManagerMetadataIngestion(code_confluence_graph_ingestion=app.state.code_confluence_graph_ingestion)
    activities.append(codebase_package_ingestion.insert_package_manager_metadata)
    
    codebase_processing_activity = CodebaseProcessingActivity(code_confluence_graph_ingestion=app.state.code_confluence_graph_ingestion)
    activities.append(codebase_processing_activity.process_codebase)

    asyncio.create_task(run_worker(activities=activities, client=app.state.temporal_client, activity_executor=app.state.activity_executor))
    yield
    await app.state.code_confluence_graph_ingestion.close()


app = FastAPI(lifespan=lifespan)


# Create background task for workflow completion
async def monitor_workflow(workflow_handle: WorkflowHandle):
    try:
        result = await workflow_handle.result()
        logger.info(f"Workflow completed with result: {result}")
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
    

@app.post("/ingest-token", status_code=201)
async def ingest_token(authorization: str = Header(...), session: Session = Depends(get_session)) -> Dict[str, str]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token: str = authorization[7:].strip()  # Remove 'Bearer '
    
    try:
        # Encrypt the token (this is non-deterministic, so we'll ignore matching by it)
        encrypted_token: str = encrypt_token(token)
        current_time: datetime = datetime.now(timezone.utc)
        
        credential: Optional[Credentials] = session.exec(select(Credentials)).first()
        
        if credential is not None:
            raise HTTPException(status_code=409, detail="Token already ingested. Use update-token to update it.")
        
        credential = Credentials(token_hash=encrypted_token, created_at=current_time)
        session.add(credential)
        
        session.commit()
        session.refresh(credential)
        return {"message": "Token ingested successfully."}
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions directly
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to process token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process authentication token")

@app.put("/update-token", status_code=200)
async def update_token(authorization: str = Header(...), session: Session = Depends(get_session)) -> Dict[str, str]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token: str = authorization[7:].strip()
    try:
        encrypted_token: str = encrypt_token(token)
        current_time: datetime = datetime.now(timezone.utc)
        
        credential: Optional[Credentials] = session.exec(select(Credentials)).first()
        if credential is None:
            raise HTTPException(status_code=404, detail="No token found to update")
        
        credential.token_hash = encrypted_token
        credential.updated_at = current_time
        session.add(credential)
        session.commit()
        session.refresh(credential)
        return {"message": "Token updated successfully."}
    except Exception as e:
        logger.error(f"Failed to update token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update authentication token")

@app.get("/repos", response_model=List[GitHubRepoSummary])
async def get_repos(session: Session = Depends(get_session)) -> List[GitHubRepoSummary]:
    # Attempt to fetch the stored credentials from the database
    try:
        credential: Optional[Credentials] = session.exec(select(Credentials)).first()
    except Exception as db_error:
        logger.error(f"Database error while fetching credentials: {db_error}")
        raise HTTPException(status_code=500, detail="Database error while fetching credentials")
    
    if not credential:
        raise HTTPException(status_code=404, detail="No credentials found")

    # Attempt to decrypt the stored token
    try:
        token: str = decrypt_token(credential.token_hash)
    except Exception as decrypt_error:
        logger.error(f"Failed to decrypt token: {decrypt_error}")
        raise HTTPException(status_code=500, detail="Internal error during authentication token decryption")
    
    # Fetch repositories from GitHub using the decrypted token
    async with httpx.AsyncClient() as client:
        headers: Dict[str, str] = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Unoplat Code Confluence"
        }
        response = await client.get("https://api.github.com/user/repos?visibility=all&per_page=100&page=1", headers=headers)
        if response.status_code != 200:
            logger.error(f"GitHub API error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="GitHub API error: failed to fetch repositories")
        
        repos_data = response.json()

    # Process and return the repository summaries
    repos_list: List[GitHubRepoSummary] = []
    for item in repos_data:
        owner_data = item.get("owner", {})
        repo_summary = GitHubRepoSummary(
            name=item.get("name"),
            owner_url=owner_data.get("html_url"),
            private=item.get("private"),
            git_url=item.get("git_url"),
            owner_name=owner_data.get("login")
        )
        repos_list.append(repo_summary)
        
    return repos_list

@app.post("/start-ingestion", status_code=201)
async def ingestion(repository: RepositorySettings, authorization: Optional[str] = Header(None)):
    """
    Start the ingestion workflow.
    """

    # Extract GitHub token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    github_token = authorization.replace("Bearer ", "")

    # Start the workflow
    workflow_handle = await start_workflow(app.state.temporal_client, repository, github_token)

    # Wait for the workflow to complete if needed
    asyncio.create_task(monitor_workflow(workflow_handle))

    logger.info(f"Started workflow. Workflow ID: {workflow_handle.id}, RunID {workflow_handle.result_run_id}")

    return {"workflow_id": workflow_handle.id, "run_id": workflow_handle.result_run_id}

