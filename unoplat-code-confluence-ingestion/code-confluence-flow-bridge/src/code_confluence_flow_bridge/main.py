# Local application imports
from src.code_confluence_flow_bridge.logging.log_config import setup_logging
from src.code_confluence_flow_bridge.logging.trace_utils import trace_id_var
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings, ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.models.github.github_repo import (
    CodebaseConfig,
    GitHubRepoRequestConfiguration,
    GitHubRepoResponseConfiguration,
    GitHubRepoSummary,
    JobStatus,
    PaginatedResponse,
    ParentWorkflowJobListResponse,
    ParentWorkflowJobResponse,
)
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import RepoWorkflowRunEnvelope
from src.code_confluence_flow_bridge.processor.activity_inbound_interceptor import ActivityStatusInterceptor
from src.code_confluence_flow_bridge.processor.codebase_child_workflow import CodebaseChildWorkflow
from src.code_confluence_flow_bridge.processor.codebase_processing.codebase_processing_activity import CodebaseProcessingActivity
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion
from src.code_confluence_flow_bridge.processor.db.postgres.child_workflow_db_activity import ChildWorkflowDbActivity
from src.code_confluence_flow_bridge.processor.db.postgres.credentials import Credentials
from src.code_confluence_flow_bridge.processor.db.postgres.db import create_db_and_tables, get_session
from src.code_confluence_flow_bridge.processor.db.postgres.flags import Flag
from src.code_confluence_flow_bridge.processor.db.postgres.parent_workflow_db_activity import ParentWorkflowDbActivity
from src.code_confluence_flow_bridge.processor.db.postgres.repository_data import Repository, RepositoryWorkflowRun
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import ConfluenceGitGraph
from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import PackageManagerMetadataIngestion
from src.code_confluence_flow_bridge.processor.parent_workflow_interceptor import ParentWorkflowStatusInterceptor
from src.code_confluence_flow_bridge.processor.repo_workflow import RepoWorkflow
from src.code_confluence_flow_bridge.utility.deps import trace_dependency
from src.code_confluence_flow_bridge.utility.password_utils import decrypt_token, encrypt_token

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Standard library imports
from datetime import datetime, timezone
import json
from typing import Any, Callable, Dict, List, Optional, Sequence, cast

# Third-party imports
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from gql import Client as GQLClient, gql
from gql.transport.aiohttp import AIOHTTPTransport
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, selectinload
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlmodel import select
from temporalio.client import Client, WorkflowHandle
from temporalio.worker import Worker

# Setup logging
logger = setup_logging(service_name="code-confluence-flow-bridge", app_name="unoplat-code-confluence")


#setup supertokens



async def get_temporal_client() -> Client:
    """Create and return a Temporal client instance."""
    # Connect to local temporal server
    # Read from env - TEMPORAL_SERVER_ADDRESS, default to localhost:7233
    temporal_server: str = os.getenv("TEMPORAL_SERVER_ADDRESS", "localhost:7233")
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
    worker = Worker(
        client,
        task_queue="unoplat-code-confluence-repository-context-ingestion",
        workflows=[RepoWorkflow, CodebaseChildWorkflow],
        activities=activities,
        activity_executor=activity_executor,
        interceptors=[ParentWorkflowStatusInterceptor(),ActivityStatusInterceptor()],
    )

    await worker.run()


async def start_workflow(
    temporal_client: Client,
    repo_request: GitHubRepoRequestConfiguration,
    github_token: str,
    workflow_id: str,
    trace_id: str,
) -> WorkflowHandle:
    """
    Start a Temporal workflow for the given repository request and workflow id.
    """
    envelope = RepoWorkflowRunEnvelope(
        repo_request=repo_request,
        github_token=github_token,
        trace_id=trace_id
    )
    workflow_handle: WorkflowHandle = await temporal_client.start_workflow(
        RepoWorkflow.run,
        arg=envelope,
        id=workflow_id,
        task_queue="unoplat-code-confluence-repository-context-ingestion"
    )
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
    
    parent_workflow_db_activity: ParentWorkflowDbActivity = ParentWorkflowDbActivity()
    activities.append(parent_workflow_db_activity.update_repository_workflow_status)
    
    child_workflow_db_activity = ChildWorkflowDbActivity()
    activities.append(child_workflow_db_activity.update_codebase_workflow_status)

    package_metadata_activity = PackageMetadataActivity()
    activities.append(package_metadata_activity.get_package_metadata)

    confluence_git_graph = ConfluenceGitGraph(code_confluence_graph_ingestion=app.state.code_confluence_graph_ingestion)
    activities.append(confluence_git_graph.insert_git_repo_into_graph_db)

    codebase_package_ingestion = PackageManagerMetadataIngestion(code_confluence_graph_ingestion=app.state.code_confluence_graph_ingestion)
    activities.append(codebase_package_ingestion.insert_package_manager_metadata)
    
    codebase_processing_activity = CodebaseProcessingActivity(code_confluence_graph_ingestion=app.state.code_confluence_graph_ingestion)
    activities.append(codebase_processing_activity.process_codebase)
    
    # Create database tables during startup
    await create_db_and_tables()
    
    asyncio.create_task(run_worker(activities=activities, client=app.state.temporal_client, activity_executor=app.state.activity_executor))
    yield
    await app.state.code_confluence_graph_ingestion.close()



app = FastAPI(lifespan=lifespan)

# Configure CORS
origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],        # Allows all methods
    allow_headers=["*"],        # Allows all headers
)


# Create background task for workflow completion
async def monitor_workflow(workflow_handle: WorkflowHandle):
    try:
        result = await workflow_handle.result()
        logger.info(f"Workflow completed with result: {result}")
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
    

@app.post("/ingest-token", status_code=201)
async def ingest_token(authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> Dict[str, str]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token: str = authorization[7:].strip()  # Remove 'Bearer '
    
    try:
        # Encrypt the token (this is non-deterministic, so we'll ignore matching by it)
        encrypted_token: str = encrypt_token(token)
        current_time: datetime = datetime.now(timezone.utc)
        
        result = await session.execute(select(Credentials))
        credential: Optional[Credentials] = result.scalars().first()
        
        if credential is not None:
            raise HTTPException(status_code=409, detail="Token already ingested. Use update-token to update it.")
        
        credential = Credentials(token_hash=encrypted_token, created_at=current_time)
        session.add(credential)
        
        # Set the isTokenSubmitted flag to true
        flag_result = await session.execute(select(Flag).where(Flag.name == "isTokenSubmitted")) #type: ignore
        token_flag: Optional[Flag] = flag_result.scalar_one_or_none()
        
        if token_flag is None:
            # Create the flag if it doesn't exist
            token_flag = Flag(name="isTokenSubmitted", status=True)
        else:
            # Update existing flag
            token_flag.status = True
            
        session.add(token_flag)
        
        await session.commit()
        await session.refresh(credential)
        
        return {"message": "Token ingested successfully."}
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions directly
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to process token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process authentication token")

@app.put("/update-token", status_code=200)
async def update_token(authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> Dict[str, str]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token: str = authorization[7:].strip()
    try:
        encrypted_token: str = encrypt_token(token)
        current_time: datetime = datetime.now(timezone.utc)
        
        result = await session.execute(select(Credentials))
        credential: Optional[Credentials] = result.scalars().first()
        if credential is None:
            raise HTTPException(status_code=404, detail="No token found to update")
        
        credential.token_hash = encrypted_token
        credential.updated_at = current_time
        session.add(credential)
        
        await session.commit()
        await session.refresh(credential)
        return {"message": "Token updated successfully."}
    except Exception as e:
        logger.error(f"Failed to update token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update authentication token")

@app.delete("/delete-token", status_code=200)
async def delete_token(session: AsyncSession = Depends(get_session)) -> Dict[str, str]:
    try:
        # Find existing credential
        result = await session.execute(select(Credentials))
        credential: Optional[Credentials] = result.scalars().first()
        if credential is None:
            raise HTTPException(status_code=404, detail="No token found to delete")
        
        await session.delete(credential)
        
        # Set the isTokenSubmitted flag to false
        flag_result = await session.execute(select(Flag).where(Flag.name == "isTokenSubmitted"))
        token_flag: Optional[Flag] = flag_result.scalar_one_or_none()
        
        if token_flag is None:
            # Create the flag if it doesn't exist
            token_flag = Flag(name="isTokenSubmitted", status=False)
        else:
            # Update existing flag
            token_flag.status = False
            
        session.add(token_flag)
        
        await session.commit()
        
        return {"message": "Token deleted successfully."}
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions directly
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to delete token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete authentication token")



@app.get("/repos", response_model=PaginatedResponse)
async def get_repos(
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    filterValues: Optional[str] = Query(None, description="Optional JSON filter values to filter repositories"),
    session: AsyncSession = Depends(get_session)
) -> PaginatedResponse:
    # Attempt to fetch the stored credentials from the database
    try:
        result = await session.execute(select(Credentials))
        credential: Optional[Credentials] = result.scalars().first()
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
    
    
    # Parse filterValues if provided, and merge with the search parameter
    filter_values_dict: dict = {}
    if filterValues:
        try:
            filter_values_dict = json.loads(filterValues)
        except Exception as e:
            logger.error(f"Invalid JSON in filterValues: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in filterValues query parameter")
    if "name" in filter_values_dict:
        search_query = filter_values_dict["name"]
    else:
        search_query = None
    
    # Fetch repositories using GraphQL
    try:
        # Create a GraphQL client with proper authentication
        transport = AIOHTTPTransport(
            url="https://api.github.com/graphql",
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "Unoplat Code Confluence"
            }
        )
        
        async with GQLClient(
            transport=transport,
            fetch_schema_from_transport=False,
        ) as client:
            if search_query:
                # Use the search query when search parameter is provided
                query = gql(
                    """
                    query SearchRepositories($query: String!, $first: Int!, $after: String) {
                        search(query: $query, type: REPOSITORY, first: $first, after: $after) {
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                            nodes {
                                ... on Repository {
                                    name
                                    isPrivate
                                    url
                                    owner {
                                        login
                                        url
                                    }
                                }
                            }
                        }
                    }
                    """
                )
                
                # Execute the search query with variables
                result = await client.execute(query, variable_values={
                    "query": search_query,
                    "first": per_page,
                    "after": cursor
                })
                
                # Process the search result
                repos_data = result["search"]["nodes"] #type: ignore
                has_next = result["search"]["pageInfo"]["hasNextPage"] #type: ignore
                next_cursor = result["search"]["pageInfo"]["endCursor"] #type: ignore
            else:
                # Use the original viewer.repositories query when no search is provided
                query = gql(
                    """
                    query GetRepositories($first: Int!, $after: String) {
                        viewer {
                            repositories(
                                first: $first,
                                affiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER],
                                after: $after
                            ) {
                                pageInfo {
                                    endCursor
                                    hasNextPage
                                }
                                nodes {
                                    name
                                    isPrivate
                                    url
                                    owner {
                                        login
                                        url
                                    }
                                }
                            }
                        }
                    }
                    """
                )
                
                # Execute the query with variables
                result = await client.execute(query, variable_values={
                    "first": per_page,
                    "after": cursor
                })
                
                # Process the result
                repos_data = result["viewer"]["repositories"]["nodes"] #type: ignore
                has_next = result["viewer"]["repositories"]["pageInfo"]["hasNextPage"] #type: ignore
                next_cursor = result["viewer"]["repositories"]["pageInfo"]["endCursor"] #type: ignore
            
            # Convert to GitHubRepoSummary objects
            repos_list: List[GitHubRepoSummary] = []
            for item in repos_data:
                repo_summary = GitHubRepoSummary(
                    name=item["name"],
                    owner_url=item["owner"]["url"],
                    private=item["isPrivate"],
                    git_url=item["url"],
                    owner_name=item["owner"]["login"]
                )
                repos_list.append(repo_summary)
            
            # Return paginated response with cursor as metadata
            return PaginatedResponse(
                items=repos_list,
                per_page=per_page,
                has_next=has_next,
                next_cursor=next_cursor
            )
            
    except Exception as e:
        logger.error(f"GraphQL Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch repositories: {str(e)}")

@app.post("/start-ingestion", status_code=201)
async def ingestion(
    repo_request: GitHubRepoRequestConfiguration,
    session: AsyncSession = Depends(get_session),
    request_logger: "Logger" = Depends(trace_dependency) # type: ignore
) -> dict[str, str]:
    """
    Start the ingestion workflow for the entire repository using the GitHub token from the database.
    Submits the whole repo_request at once to the Temporal workflow.
    Returns the workflow_id and run_id.
    Also ingests the repository configuration into the database.
    """
    # Attempt to fetch the stored credentials from the database
    try:
        result = await session.execute(select(Credentials))
        credential: Optional[Credentials] = result.scalars().first()
    except Exception as db_error:
        request_logger.error(f"Database error while fetching credentials: {db_error}")
        raise HTTPException(status_code=500, detail="Database error while fetching credentials")

    if not credential:
        raise HTTPException(status_code=404, detail="No credentials found")

    # Attempt to decrypt the stored token
    try:
        github_token: str = decrypt_token(credential.token_hash)
    except Exception as decrypt_error:
        request_logger.error(f"Failed to decrypt token: {decrypt_error}")
        raise HTTPException(status_code=500, detail="Internal error during authentication token decryption")

    # Fetch the trace-id that `trace_dependency` already set
    trace_id = trace_id_var.get()
    if not trace_id:
        raise HTTPException(500, "trace_id not set by dependency")

    # Start the Temporal workflow
    workflow_handle: WorkflowHandle = await start_workflow(
        temporal_client=app.state.temporal_client,
        repo_request=repo_request,
        github_token=github_token,
        workflow_id=f"ingest-{trace_id}",
        trace_id=trace_id,
    )
    # Schedule background monitoring immediately after starting the workflow
    asyncio.create_task(monitor_workflow(workflow_handle))
    # Extract the run_id for response and status tracking
    run_id: str = workflow_handle.result_run_id or "none"
    

    request_logger.info(f"Started workflow. Workflow ID: {workflow_handle.id}, RunID {workflow_handle.result_run_id}")
    return {
        "workflow_id": workflow_handle.id or "none",
        "run_id": run_id
    }

@app.get("/flags/{flag_name}", status_code=200)
async def get_flag_status(flag_name: str, session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    """
    Get the status of a specific flag by name.
    
    Args:
        flag_name (str): The name of the flag to check
        session (Session): Database session
        
    Returns:
        Dict[str, Any]: Flag information including status
    """
    try:
        result = await session.execute(select(Flag).where(Flag.name == flag_name))
        flag: Optional[Flag] = result.scalar_one_or_none()
        if flag is None:
            raise HTTPException(status_code=404, detail=f"Flag '{flag_name}' not found")
        return {
            "name": flag.name,
            "status": flag.status,
            "exists": True
        }
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions directly
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to get flag status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get flag status for {flag_name}")

@app.get("/flags", status_code=200)
async def get_all_flags(session: AsyncSession = Depends(get_session)) -> List[Dict[str, Any]]:
    """
    Get the status of all available flags.
    
    Args:
        session (Session): Database session
        
    Returns:
        List[Dict[str, Any]]: List of flag information
    """
    try:
        result = await session.execute(select(Flag))
        flags: Sequence[Flag] = result.scalars().all()
        return [
            {
                "name": flag.name,
                "status": flag.status
            }
            for flag in flags
        ]
    except Exception as e:
        logger.error(f"Failed to get flags: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get flags")

@app.put("/flags/{flag_name}", status_code=200)
async def set_flag_status(flag_name: str, status: bool, session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    """
    Set the status of a specific flag by name.
    
    Args:
        flag_name (str): The name of the flag to set
        status (bool): The status to set for the flag
        session (Session): Database session
        
    Returns:
        Dict[str, Any]: Updated flag information
    """
    try:
        result = await session.execute(select(Flag).where(Flag.name == flag_name)) 
        flag: Optional[Flag] = result.scalar_one_or_none()
        
        if flag is None:
            # Create the flag if it doesn't exist
            flag = Flag(name=flag_name, status=status)
        else:
            # Update existing flag
            flag.status = status
            
        session.add(flag)
        await session.commit()
        await session.refresh(flag)
        
        return {
            "name": flag.name,
            "status": flag.status
        }
    except Exception as e:
        logger.error(f"Failed to set flag status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set flag status for {flag_name}")

# @app.put("/repository-data", status_code=200)
# async def update_repository_data(
#     repo_config: GitHubRepoRequestConfiguration,
#     session: Session = Depends(get_session)
# ) -> dict:
#     db_obj: RepositoryData | None = session.get(RepositoryData, repo_config.repository_name)
#     if not db_obj:
#         raise HTTPException(status_code=404, detail="Repository data not found for this name.")
#     db_obj.repository_metadata = jsonable_encoder([
#         CodebaseRepoConfig(**c.model_dump()) for c in repo_config.repository_metadata
#     ])
#     session.add(db_obj)
#     session.commit()
#     session.refresh(db_obj)
#     return {"message": "Repository data updated successfully."}

# @app.get(
#     "/repository-status",
#     response_model=GithubRepoStatus,
# )
# async def get_repository_status(
#     repository_name: str = Query(..., description="The name of the repository"),
#     repository_owner_name: str = Query(..., description="The name of the repository owner"),
#     workflow_run_id: Optional[str] = Query(None, description="Optional workflow run ID to fetch specific status"),
#     session: AsyncSession = Depends(get_session),
# ) -> GithubRepoStatus:
#     """
#     Get the current status of a repository workflow run and its associated codebase runs.
#     If workflow_run_id is provided, fetch that specific run, otherwise fetch the latest running workflow.
#     """
#     try:
#         # Build base query for repository workflow run
#         stmt = select(RepositoryWorkflowRun).where(
#             RepositoryWorkflowRun.repository_name == repository_name,
#             RepositoryWorkflowRun.repository_owner_name == repository_owner_name,
#         )
        
#         # If specific workflow_run_id provided, use it, otherwise get latest RUNNING workflow
#         if workflow_run_id:
#             stmt = stmt.where(RepositoryWorkflowRun.repository_workflow_run_id == workflow_run_id)
#         else:
#             stmt = stmt.where(RepositoryWorkflowRun.status == JobStatus.RUNNING.value)
        
#         # Order by latest started_at and get the first one
#         stmt = stmt.order_by(desc(RepositoryWorkflowRun.started_at)).limit(1)
        
#         parent_run = (await session.execute(stmt)).scalar_one_or_none()
#         if not parent_run:
#             if workflow_run_id:
#                 error_msg = f"Workflow run {workflow_run_id} not found for {repository_name}/{repository_owner_name}"
#             else:
#                 error_msg = f"No running workflow found for {repository_name}/{repository_owner_name}"
#             raise HTTPException(status_code=404, detail=error_msg)
        
#         # Fetch all codebase workflow runs associated with this parent run
#         cb_stmt = select(CodebaseWorkflowRun).where(
#             CodebaseWorkflowRun.repository_name == repository_name,
#             CodebaseWorkflowRun.repository_owner_name == repository_owner_name,
#             CodebaseWorkflowRun.repository_workflow_run_id == parent_run.repository_workflow_run_id,
#         )
#         codebase_runs = (await session.execute(cb_stmt)).scalars().all()
        
#         # Map to Pydantic models
#         codebase_statuses = []
#         for run in codebase_runs:
#             error_report = ErrorReport(**run.error_report) if run.error_report else None
#             codebase_statuses.append(
#                 CodebaseCurrentStatus(
#                     root_package=run.root_package,
#                     codebase_workflow_run_id=run.codebase_workflow_run_id,
#                     codebase_workflow_id=run.codebase_workflow_id,
#                     status=JobStatus(run.status),
#                     started_at=run.started_at,
#                     completed_at=run.completed_at,
#                     error_report=error_report,
#                 )
#             )
        
#         # Create parent repository status object
#         return GithubRepoStatus(
#             repository_name=parent_run.repository_name,
#             repository_owner_name=parent_run.repository_owner_name,
#             repository_workflow_run_id=parent_run.repository_workflow_run_id,
#             repository_workflow_id=parent_run.repository_workflow_id,
#             status=JobStatus(parent_run.status),
#             started_at=parent_run.started_at,
#             completed_at=parent_run.completed_at,
#             error_report=ErrorReport(**parent_run.error_report) if parent_run.error_report else None,
#             codebase_statuses=codebase_statuses,
#         )
#     except Exception as e:
#         logger.error(f"Error retrieving repository status: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error retrieving repository status: {str(e)}"
#         )

@app.get(
    "/repository-data",
    response_model=GitHubRepoResponseConfiguration,
)
async def get_repository_data(
    repository_name: str = Query(..., description="The name of the repository"),
    repository_owner_name: str = Query(..., description="The name of the repository owner"),
    session: AsyncSession = Depends(get_session),
) -> GitHubRepoResponseConfiguration:
    # fetch repository record with its codebase configs
    db_obj: Repository | None = await session.get(
        Repository,
        (repository_name, repository_owner_name),
        options=[
            selectinload(
                cast(QueryableAttribute[Any], Repository.configs)
            )
        ]
    )
    if not db_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Repository data not found for {repository_name}/{repository_owner_name}"
        )

    # Map database CodebaseConfig entries to Pydantic models
    try:
        codebases = [
            CodebaseConfig(
                codebase_folder=config.source_directory,
                root_package=config.root_package,
                programming_language_metadata=ProgrammingLanguageMetadata(
                    language=config.programming_language_metadata["language"],
                    package_manager=config.programming_language_metadata["package_manager"],
                    language_version=config.programming_language_metadata.get("language_version"),
                ),
            )
            for config in db_obj.configs
        ]
        
        return GitHubRepoResponseConfiguration(
            repository_name=db_obj.repository_name,
            repository_owner_name=db_obj.repository_owner_name,
            repository_metadata=codebases,
        )
    except Exception as e:
        logger.error(f"Error mapping repository data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing repository data for {repository_name}/{repository_owner_name}"
        )

@app.get(
    "/parent-workflow-jobs",
    response_model=ParentWorkflowJobListResponse,
    description="Get all parent workflow jobs data without pagination"
)
async def get_parent_workflow_jobs(session: AsyncSession = Depends(get_session)) -> ParentWorkflowJobListResponse:
    """Get all parent workflow jobs data without pagination.
    
    Returns job information for all parent workflows (RepositoryWorkflowRun).
    Includes repository_name, repository_owner_name, repository_workflow_run_id, status, started_at, completed_at.
    """
    try:
        # Query to get all parent workflow jobs (RepositoryWorkflowRun records)
        query = select(RepositoryWorkflowRun)
        result = await session.execute(query)
        workflow_runs = result.scalars().all()
        
        # Transform the database records to the response model format
        jobs = [
            ParentWorkflowJobResponse(
                repository_name=run.repository_name,
                repository_owner_name=run.repository_owner_name,
                repository_workflow_run_id=run.repository_workflow_run_id,
                status=JobStatus(run.status),
                started_at=run.started_at,
                completed_at=run.completed_at
            ) for run in workflow_runs
        ]
        
        return ParentWorkflowJobListResponse(jobs=jobs)
    except Exception as e:
        logger.error(f"Error retrieving parent workflow jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving parent workflow jobs: {str(e)}"
        )

@app.get("/user-details", status_code=200)
async def get_user_details(session: AsyncSession = Depends(get_session)) -> Dict[str, Optional[str]]:
    """
    Fetch authenticated GitHub user's name, avatar URL, and email.
    """
    # Fetch stored GitHub token from database
    result = await session.execute(select(Credentials))
    credential: Optional[Credentials] = result.scalars().first()
    if not credential:
        raise HTTPException(status_code=404, detail="No credentials found")
    token = decrypt_token(credential.token_hash)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient() as client:
        # Primary user info
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        if user_resp.status_code != 200:
            raise HTTPException(status_code=user_resp.status_code, detail="Failed to fetch user info")
        user_data = user_resp.json()

        # Determine email: use public email or fetch primary email via separate endpoint
        email = user_data.get("email")
        if not email:
            emails_resp = await client.get("https://api.github.com/user/emails", headers=headers)
            if emails_resp.status_code == 200:
                emails = emails_resp.json()
                primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                email = primary

    return {
        "name": user_data.get("name"),
        "avatar_url": user_data.get("avatar_url"),
        "email": email,
    }