import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.concurrency import asynccontextmanager
from loguru import logger
from temporalio.client import Client, WorkflowHandle
from temporalio.worker import Worker

from src.code_confluence_flow_bridge.logging.log_config import setup_logging
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings, RepositorySettings
from src.code_confluence_flow_bridge.processor.codebase_child_workflow import CodebaseChildWorkflow
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import ConfluenceGitGraph
from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
from src.code_confluence_flow_bridge.processor.repo_workflow import RepoWorkflow

# Setup logging
logger = setup_logging()

async def get_temporal_client() -> Client:
    """Create and return a Temporal client instance."""
    # Connect to local temporal server
    # Read from env - TEMPORAL_SERVER_ADDRESS, default to localhost:7233
    temporal_server = os.getenv("TEMPORAL_SERVER_ADDRESS", "localhost:7233")
    temporal_client = await Client.connect(temporal_server)
    return temporal_client


async def run_worker(gitActivity: GitActivity,package_metadata_child_activity: PackageMetadataActivity,confluence_git_graph: ConfluenceGitGraph,client: Client, activity_executor):
    worker = Worker(
        client,
        task_queue="unoplat-code-confluence-repository-context-ingestion",
        workflows=[RepoWorkflow,CodebaseChildWorkflow],
        activities=[gitActivity.process_git_activity,package_metadata_child_activity.run,confluence_git_graph.insert_git_repo_into_graph_db],
        activity_executor=activity_executor
    )
    
    # Run the worker in the background
    await worker.run()    
     


async def start_workflow(temporal_client: Client, repository: RepositorySettings, github_token: str):
    workflow_handle = await temporal_client.start_workflow(
        RepoWorkflow.run,
        args=(repository, github_token),
        id=repository.git_url,
        task_queue="unoplat-code-confluence-repository-context-ingestion"
    )
    logger.info(f"Started workflow. Workflow ID: {workflow_handle.id}, RunID {workflow_handle.result_run_id}")
    return workflow_handle    
    
# Create FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.code_confluence_env = EnvironmentSettings()
    app.state.temporal_client = await get_temporal_client()
    app.state.git_activity = GitActivity()
    app.state.activity_executor = ThreadPoolExecutor()
    app.state.package_metadata_activity = PackageMetadataActivity()
    app.state.confluence_git_graph = ConfluenceGitGraph(code_confluence_env=app.state.code_confluence_env)
    asyncio.create_task(run_worker(gitActivity=app.state.git_activity,package_metadata_child_activity=app.state.package_metadata_activity,confluence_git_graph=app.state.confluence_git_graph,client=app.state.temporal_client, activity_executor=app.state.activity_executor))
    #await worker_task
    yield    

app = FastAPI(lifespan=lifespan)
    


# Create background task for workflow completion
async def monitor_workflow(workflow_handle: WorkflowHandle):
    try:
        result = await workflow_handle.result()
        logger.info(f"Workflow completed with result: {result}")
    except Exception as e:
        logger.error(f"Workflow failed: {e}")

    

@app.post("/start-ingestion", status_code=201)
async def ingestion(repository: RepositorySettings,authorization: Optional[str] = Header(None)):
    """
    Start the ingestion workflow.
    """

    # Extract GitHub token from Authorization header
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )
    
    github_token = authorization.replace('Bearer ', '')

    # Start the workflow
    workflow_handle = await start_workflow(app.state.temporal_client, repository, github_token)
    
    # Wait for the workflow to complete if needed
    asyncio.create_task(monitor_workflow(workflow_handle))
    
    logger.info(f"Started workflow. Workflow ID: {workflow_handle.id}, RunID {workflow_handle.result_run_id}")
    
    return {"workflow_id": workflow_handle.id, "run_id": workflow_handle.result_run_id}



# Create FastAPI application

        

    

    

