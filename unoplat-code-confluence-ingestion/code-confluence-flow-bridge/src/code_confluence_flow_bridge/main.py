import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.concurrency import asynccontextmanager
from loguru import logger
from temporalio.client import Client, WorkflowHandle
from temporalio.worker import Worker

from src.code_confluence_flow_bridge.models.configuration.settings import RepositorySettings
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity
from src.code_confluence_flow_bridge.processor.repo_workflow import RepoWorkflow


async def get_temporal_client() -> Client:
    """Create and return a Temporal client instance."""
    # Connect to local temporal server
    temporal_client = await Client.connect("localhost:7233")
    return temporal_client


async def run_worker(gitActivity: GitActivity,client: Client, activity_executor):
    worker = Worker(
        client,
        task_queue="unoplat-code-confluence-repository-context-ingestion",
        workflows=[RepoWorkflow],
        activities=[gitActivity.process_git_activity],
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
    
    app.state.temporal_client = await get_temporal_client()
    app.state.git_activity = GitActivity()
    app.state.activity_executor = ThreadPoolExecutor()
    asyncio.create_task(run_worker(app.state.git_activity,app.state.temporal_client, app.state.activity_executor))
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

        

    

    

