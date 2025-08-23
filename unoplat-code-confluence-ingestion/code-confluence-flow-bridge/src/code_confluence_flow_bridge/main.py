import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import traceback
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    cast,
)

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from github import Github
from gql import Client as GQLClient, gql
from gql.transport.aiohttp import AIOHTTPTransport
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, selectinload
from sqlmodel import select
from sse_starlette.sse import EventSourceResponse
from temporalio.client import Client, WorkflowHandle
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import ApplicationError
from temporalio.worker import PollerBehaviorAutoscaling, Worker
from unoplat_code_confluence_commons.base_models import (
    CodebaseWorkflowRun,
    Credentials,
    ProgrammingLanguageMetadata,
    Repository,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.security import (
    decrypt_token,
    encrypt_token,
)

from src.code_confluence_flow_bridge.logging.log_config import setup_logging
from src.code_confluence_flow_bridge.logging.trace_utils import (
    build_trace_id,
    trace_id_var,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.models.github.github_repo import (
    CodebaseConfig,
    CodebaseStatus,
    CodebaseStatusList,
    ErrorReport,
    GithubIssueSubmissionRequest,
    GitHubRepoRequestConfiguration,
    GitHubRepoResponseConfiguration,
    GithubRepoStatus,
    GitHubRepoSummary,
    IngestedRepositoriesListResponse,
    IngestedRepositoryResponse,
    IssueStatus,
    IssueTracking,
    IssueType,
    JobStatus,
    PaginatedResponse,
    ParentWorkflowJobListResponse,
    ParentWorkflowJobResponse,
    RefreshRepositoryResponse,
    WorkflowRun,
    WorkflowStatus,
)
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
    RepoWorkflowRunEnvelope,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.progress_models import (
    DetectionResult,
    DetectionState,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.python_ripgrep_detector import (
    PythonRipgrepDetector,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.sse_response import (
    SSEMessage,
)
from src.code_confluence_flow_bridge.processor.activity_inbound_interceptor import (
    ActivityStatusInterceptor,
)
from src.code_confluence_flow_bridge.processor.codebase_child_workflow import (
    CodebaseChildWorkflow,
)
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import (
    CodeConfluenceGraph,
)
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_deletion import (
    CodeConfluenceGraphDeletion,
)
from src.code_confluence_flow_bridge.processor.db.postgres.child_workflow_db_activity import (
    ChildWorkflowDbActivity,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import (
    create_db_and_tables,
    dispose_current_engine,
    get_session,
    get_session_cm,
)
from src.code_confluence_flow_bridge.processor.db.postgres.flags import Flag
from src.code_confluence_flow_bridge.processor.db.postgres.framework_loader import (
    FrameworkDefinitionLoader,
)
from src.code_confluence_flow_bridge.processor.db.postgres.parent_workflow_db_activity import (
    ParentWorkflowDbActivity,
)
from src.code_confluence_flow_bridge.processor.generic_codebase_processing_activity import (
    GenericCodebaseProcessingActivity,
)
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import (
    GitActivity,
)
from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import (
    ConfluenceGitGraph,
)
from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import (
    PackageMetadataActivity,
)
from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import (
    PackageManagerMetadataIngestion,
)
from src.code_confluence_flow_bridge.processor.parent_workflow_interceptor import (
    ParentWorkflowStatusInterceptor,
)
from src.code_confluence_flow_bridge.processor.repo_workflow import RepoWorkflow
from src.code_confluence_flow_bridge.utility.deps import trace_dependency
from src.code_confluence_flow_bridge.utility.environment_utils import (
    construct_local_repository_path,
    get_runtime_environment,
    validate_local_repository_path,
)
from src.code_confluence_flow_bridge.utility.git_remote_utils import (
    extract_github_organization_from_local_repo,
)

# Setup logging - override imported logger with configured one
logger = setup_logging(
    service_name="code-confluence-flow-bridge", app_name="unoplat-code-confluence"
)


# setup supertokens


async def get_temporal_client() -> Client:
    """Create and return a Temporal client instance."""
    # Connect to local temporal server
    # Read from env - TEMPORAL_SERVER_ADDRESS, default to localhost:7233
    temporal_server: str = os.getenv("TEMPORAL_SERVER_ADDRESS", "localhost:7233")
    temporal_client = await Client.connect(
        temporal_server, data_converter=pydantic_data_converter
    )
    return temporal_client


async def _serve_worker(stop: asyncio.Event, worker: Worker) -> None:
    """Keep the worker running until `stop` is set, then shut it down."""
    async with worker:
        await stop.wait()  # blocks here
    # context manager calls worker.shutdown() for us


def create_worker(
    activities: List[Callable],
    client: Client,
    activity_executor: ThreadPoolExecutor,
    env_settings: EnvironmentSettings,
) -> Worker:
    """
    Create a Temporal worker with given activities

    Args:
        activities: List of activity functions
        client: Temporal client
        activity_executor: Thread pool executor for activities
        env_settings: Environment settings containing Temporal worker configuration

    Returns:
        Worker: Configured Temporal worker instance
    """
    try:
        # Worker configuration parameters
        worker_params = {
            "client": client,
            "task_queue": "unoplat-code-confluence-repository-context-ingestion",
            "workflows": [RepoWorkflow, CodebaseChildWorkflow],
            "activities": activities,
            "activity_executor": activity_executor,
            "interceptors": [
                ParentWorkflowStatusInterceptor(),
                ActivityStatusInterceptor(),
            ],
            "max_concurrent_activities": env_settings.temporal_max_concurrent_activities,
        }

        # Configure poller behaviors based on settings
        if env_settings.temporal_enable_poller_autoscaling:
            # Configure workflow task poller behavior with autoscaling
            workflow_poller = PollerBehaviorAutoscaling(
                minimum=env_settings.temporal_workflow_poller_min,
                initial=env_settings.temporal_workflow_poller_initial,
                maximum=env_settings.temporal_workflow_poller_max,
            )
            worker_params["workflow_task_poller_behavior"] = workflow_poller

            # Configure activity task poller behavior with autoscaling
            activity_poller = PollerBehaviorAutoscaling(
                minimum=env_settings.temporal_activity_poller_min,
                initial=env_settings.temporal_activity_poller_initial,
                maximum=env_settings.temporal_activity_poller_max,
            )
            worker_params["activity_task_poller_behavior"] = activity_poller

            # Log autoscaling configuration
            logger.info(
                "Starting Temporal worker with autoscaling pollers enabled. "
                "Workflow poller: min={}, initial={}, max={}. "
                "Activity poller: min={}, initial={}, max={}",
                env_settings.temporal_workflow_poller_min,
                env_settings.temporal_workflow_poller_initial,
                env_settings.temporal_workflow_poller_max,
                env_settings.temporal_activity_poller_min,
                env_settings.temporal_activity_poller_initial,
                env_settings.temporal_activity_poller_max,
            )
        else:
            # Use traditional fixed polling configuration
            worker_params["max_concurrent_activity_task_polls"] = (
                env_settings.temporal_max_concurrent_activity_task_polls
            )

            # Log standard configuration
            logger.info(
                """Starting Temporal worker with max_concurrent_activities={}, 
                max_concurrent_activity_task_polls={},
                repository base path={}""",
                env_settings.temporal_max_concurrent_activities,
                env_settings.temporal_max_concurrent_activity_task_polls,
                env_settings.repositories_base_path,
            )

        # Create the worker with client as positional argument and other parameters as keyword arguments
        if env_settings.temporal_enable_poller_autoscaling:
            # Initialize with autoscaling poller behaviors
            worker = Worker(
                client,  # Client must be passed as a positional argument
                task_queue="unoplat-code-confluence-repository-context-ingestion",
                workflows=[RepoWorkflow, CodebaseChildWorkflow],
                activities=activities,
                activity_executor=activity_executor,
                interceptors=[
                    ParentWorkflowStatusInterceptor(),
                    ActivityStatusInterceptor(),
                ],
                max_concurrent_activities=env_settings.temporal_max_concurrent_activities,
                # Configure poller behaviors with autoscaling
                workflow_task_poller_behavior=PollerBehaviorAutoscaling(
                    minimum=env_settings.temporal_workflow_poller_min,
                    initial=env_settings.temporal_workflow_poller_initial,
                    maximum=env_settings.temporal_workflow_poller_max,
                ),
                activity_task_poller_behavior=PollerBehaviorAutoscaling(
                    minimum=env_settings.temporal_activity_poller_min,
                    initial=env_settings.temporal_activity_poller_initial,
                    maximum=env_settings.temporal_activity_poller_max,
                ),
            )
        else:
            # Initialize with traditional fixed polling configuration
            worker = Worker(
                client,  # Client must be passed as a positional argument
                task_queue="unoplat-code-confluence-repository-context-ingestion",
                workflows=[RepoWorkflow, CodebaseChildWorkflow],
                activities=activities,
                activity_executor=activity_executor,
                interceptors=[
                    ParentWorkflowStatusInterceptor(),
                    ActivityStatusInterceptor(),
                ],
                max_concurrent_activities=env_settings.temporal_max_concurrent_activities,
                max_concurrent_activity_task_polls=env_settings.temporal_max_concurrent_activity_task_polls,
            )

        # Return the configured worker
        return worker

    except Exception as e:
        # Follow established error handling pattern in the codebase
        error_context = {
            "workflow_id": "worker_initialization",  # No specific workflow ID for worker initialization
            "activity_name": "run_worker",
            "error_details": str(e),
            "traceback": traceback.format_exc(),
        }

        logger.error(
            "Failed to start Temporal worker: {}",
            str(e),
            extra={"error_context": error_context},
        )

        # TODO: fix this exception this should be standard exception as worker exceptions should be application error
        error_message = "Failed to start Temporal worker: {}".format(str(e))
        raise ApplicationError(error_message, type="WORKER_INITIALIZATION_ERROR") from e


async def fetch_github_token_from_db(session: AsyncSession) -> str:
    """
    Fetch and decrypt GitHub token from database using credential_key.

    Args:
        session: Database session

    Returns:
        Decrypted GitHub token

    Raises:
        HTTPException: If no credentials found or decryption fails
    """
    try:
        result = await session.execute(
            select(Credentials).where(Credentials.credential_key == "github_pat")
        )
        credential: Optional[Credentials] = result.scalars().first()
    except Exception as db_error:
        logger.error("Database error while fetching credentials: {}", db_error)
        raise HTTPException(
            status_code=500, detail="Database error while fetching credentials"
        )

    if not credential:
        raise HTTPException(status_code=404, detail="No GitHub credentials found")

    try:
        return decrypt_token(credential.token_hash)
    except Exception as decrypt_error:
        logger.error("Failed to decrypt token: {}", decrypt_error)
        raise HTTPException(
            status_code=500,
            detail="Internal error during authentication token decryption",
        )


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
        repo_request=repo_request, github_token=github_token, trace_id=trace_id
    )
    workflow_handle: WorkflowHandle = await temporal_client.start_workflow(
        RepoWorkflow.run,
        arg=envelope,
        id=workflow_id,
        task_queue="unoplat-code-confluence-repository-context-ingestion",
    )
    logger.info(
        "Started workflow. Workflow ID: {}, RunID {}",
        workflow_handle.id,
        workflow_handle.result_run_id,
    )
    return workflow_handle


async def generate_sse_events(
    git_url: str, github_token: str, detector: PythonRipgrepDetector
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Generate SSE events for codebase detection progress (v2).

    Args:
        git_url: GitHub repository URL or local path
        github_token: GitHub authentication token
        detector: PythonRipgrepDetector instance

    Yields:
        SSE event dictionaries with event, data, and id keys
    """
    event_id = 0  # Per-request counter starting from 0
    
    # Send initial connection event
    yield SSEMessage.connected(str(event_id))
    event_id += 1

    # Send initial progress
    yield SSEMessage.format_sse(
        data={
            "state": DetectionState.INITIALIZING.value,
            "message": "Starting codebase detection...",
            "repository_url": git_url,
        },
        event="progress",
        id=str(event_id)
    )
    event_id += 1

    try:
        # Send cloning/analyzing progress based on whether it's local or remote
        if os.path.exists(git_url):
            yield SSEMessage.format_sse(
                data={
                    "state": DetectionState.ANALYZING.value,
                    "message": "Analyzing local repository...",
                    "repository_url": git_url,
                },
                event="progress",
                id=str(event_id)
            )
            event_id += 1
        else:
            yield SSEMessage.format_sse(
                data={
                    "state": DetectionState.CLONING.value,
                    "message": "Cloning repository...",
                    "repository_url": git_url,
                },
                event="progress",
                id=str(event_id)
            )
            event_id += 1

        # Run detection directly using the async method
        codebases = await detector.detect_codebases(git_url, github_token)

        # Send completion progress
        yield SSEMessage.format_sse(
            data={
                "state": DetectionState.COMPLETE.value,
                "message": f"Detection completed. Found {len(codebases)} codebases.",
                "repository_url": git_url,
            },
            event="progress",
            id=str(event_id)
        )
        event_id += 1

        # Create and send result
        result = DetectionResult(
            repository_url=git_url,
            codebases=codebases,
            error=None,
        )

        # Send result event
        yield SSEMessage.result(result.model_dump(), str(event_id))
        event_id += 1

        # Send completion event
        yield SSEMessage.done(str(event_id))

    except Exception as e:
        # Send error progress
        yield SSEMessage.format_sse(
            data={
                "state": DetectionState.COMPLETE.value,
                "message": f"Detection failed: {str(e)}",
                "repository_url": git_url,
            },
            event="progress",
            id=str(event_id)
        )
        event_id += 1

        # Create error result
        result = DetectionResult(
            repository_url=git_url,
            codebases=[],
            error=str(e),
        )

        # Send result with error
        yield SSEMessage.result(result.model_dump(), str(event_id))
        event_id += 1

        # Send error event
        logger.error("Detection error: {}", str(e))
        yield SSEMessage.error(str(e), error_type="DETECTION_ERROR", event_id=str(event_id))
        event_id += 1
        yield SSEMessage.done(str(event_id))


async def detect_codebases_sse(
    git_url: str = Query(
        ..., description="GitHub repository URL or folder name for local repository"
    ),
    is_local: bool = Query(False, description="Whether this is a local repository"),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """
    Server-Sent Events endpoint for real-time codebase detection progress (v2).

    Streams progress updates during Python codebase auto-detection from GitHub repositories
    or local Git repositories. Uses FastAPI's StreamingResponse with proper SSE formatting.

    Args:
        git_url: GitHub repository URL or folder name for local repository
        is_local: Whether this is a local repository
        session: Database session for token retrieval

    Returns:
        StreamingResponse with text/event-stream content type
    """
    # Construct appropriate path based on environment and repository type
    if is_local:
        # For local repositories, construct the full path based on runtime environment
        # git_url contains just the folder name (e.g., "dspy")
        actual_path = construct_local_repository_path(git_url)
        github_token = ""
        logger.info(
            "Local repository detection - folder: {}, resolved path: {}, environment: {}",
            git_url,
            actual_path,
            get_runtime_environment(),
        )
    else:
        # For remote repositories, git_url is the actual GitHub URL
        actual_path = git_url
        github_token = await fetch_github_token_from_db(session)
        logger.info("Remote repository detection - URL: {}", git_url)

    # Use the shared PythonCodebaseDetector instance directly
    detector = app.state.python_codebase_detector

    # Generate SSE events using the v2 helper function and return EventSourceResponse
    return EventSourceResponse(
        generate_sse_events(actual_path, github_token, detector),
        ping=15,  # Keep-alive pings every 15 seconds
        send_timeout=60,  # Timeout for send operations
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive", 
            "X-Accel-Buffering": "no", 
        },
    )


# Create FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.code_confluence_env = EnvironmentSettings()
    app.state.temporal_client = await get_temporal_client()

    # Initialize Neo4j connection and schema once during application startup
    app.state.code_confluence_graph = CodeConfluenceGraph(
        code_confluence_env=app.state.code_confluence_env
    )
    await app.state.code_confluence_graph.connect()
    await app.state.code_confluence_graph.create_schema()
    logger.info("Neo4j connection and schema initialized successfully")

    # Initialize shared PythonRipgrepDetector instance
    app.state.python_codebase_detector = PythonRipgrepDetector()
    await app.state.python_codebase_detector.initialize_rules()
    logger.info("PythonRipgrepDetector initialized successfully")

    # Initialize graph deletion service (reuses the global connection)
    app.state.code_confluence_graph_deletion = CodeConfluenceGraphDeletion(
        app.state.code_confluence_graph
    )
    # Note: Don't call initialize() on deletion service since global connection is already established

    # Calculate thread pool size based on Temporal best practice: one thread per activity slot plus a buffer
    # This ensures we have enough threads to handle all concurrent activities plus overhead
    pool_size = app.state.code_confluence_env.temporal_max_concurrent_activities + 4
    app.state.activity_executor = ThreadPoolExecutor(max_workers=pool_size)
    logger.info(
        "Initialized activity executor with {} threads (max_concurrent_activities={} + 4 buffer threads)",
        pool_size,
        app.state.code_confluence_env.temporal_max_concurrent_activities,
    )
    loop = asyncio.get_running_loop()
    loop.set_default_executor(app.state.activity_executor)
    logger.info("Set default executor for asyncio loop")

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

    # Create activities with shared graph instance for managed transactions
    confluence_git_graph = ConfluenceGitGraph(
        code_confluence_graph=app.state.code_confluence_graph
    )
    activities.append(confluence_git_graph.insert_git_repo_into_graph_db)

    codebase_package_ingestion = PackageManagerMetadataIngestion(
        code_confluence_graph=app.state.code_confluence_graph
    )
    activities.append(codebase_package_ingestion.insert_package_manager_metadata)

    # Create generic codebase processing activity with shared graph instance
    generic_activity = GenericCodebaseProcessingActivity(
        code_confluence_graph=app.state.code_confluence_graph
    )
    activities.append(generic_activity.process_codebase_generic)

    # Create database tables during startup
    await create_db_and_tables()

    # Load framework definitions at startup
    if os.getenv("LOAD_FRAMEWORK_DEFINITIONS", "true").lower() == "true":
        try:
            framework_loader = FrameworkDefinitionLoader(app.state.code_confluence_env)
            async with get_session_cm() as session:
                metrics = await framework_loader.load_framework_definitions_at_startup(
                    session
                )
                if not metrics.get("skipped"):
                    logger.info(
                        "Framework definitions loaded in {:.3f}s", metrics["total_time"]
                    )
        except Exception as e:
            logger.error("Failed to load framework definitions: {}", e)
            if os.getenv("FRAMEWORK_DEFINITIONS_REQUIRED", "false").lower() == "true":
                raise

    # Create the worker
    worker = create_worker(
        activities=activities,
        client=app.state.temporal_client,
        activity_executor=app.state.activity_executor,
        env_settings=app.state.code_confluence_env,
    )

    # Create stop event and worker task
    stop_event = asyncio.Event()
    worker_task = asyncio.create_task(_serve_worker(stop_event, worker))

    # Store references for cleanup
    app.state.worker_task = worker_task
    app.state.worker_stop = stop_event
    app.state.temporal_client = (
        app.state.temporal_client
    )  # Already assigned, but keeping for clarity
    app.state.activity_executor = (
        app.state.activity_executor
    )  # Already assigned, but keeping for clarity

    try:
        # Hand control back to FastAPI until shutdown is triggered
        yield
    finally:
        # ── shutdown ─────────────────────────────────────────────────────
        logger.info("Shutting down application...")

        # 1. Signal worker to stop
        stop_event.set()

        # 2. Wait for worker to shut down gracefully
        try:
            await worker_task
            logger.info("Temporal worker shut down successfully")
        except Exception as e:
            logger.error("Error during worker shutdown: {}", e)

        # 3. Temporal client doesn't need explicit disconnect - it cleans up on garbage collection

        # 4. Close Neo4j connections
        try:
            # Close the main graph connection first (this closes the global connection)
            await app.state.code_confluence_graph.close()
            logger.info("Neo4j global connection closed")
        except Exception as e:
            logger.error("Error closing Neo4j connections: {}", e)

        # 5. Dispose SQLAlchemy async engine
        try:
            await dispose_current_engine()
            logger.info("SQLAlchemy engine disposed")
        except Exception as exc:
            logger.warning("Failed to dispose async engine during shutdown: {}", exc)

        # 6. Shut down the thread pool executor (after worker is done)
        try:
            app.state.activity_executor.shutdown(wait=True)
            logger.info("Thread pool executor shut down")
        except Exception as e:
            logger.error("Error shutting down thread pool executor: {}", e)


app = FastAPI(lifespan=lifespan)

# Configure CORS
origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Create background task for workflow completion
async def monitor_workflow(workflow_handle: WorkflowHandle) -> None:
    try:
        result = await workflow_handle.result()
        logger.info("Workflow completed with result: {}", result)
    except Exception as e:
        logger.error("Workflow failed: {}", e)


@app.post("/ingest-token", status_code=201)
async def ingest_token(
    authorization: str = Header(...), session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token: str = authorization[7:].strip()  # Remove 'Bearer '

    try:
        # Encrypt the token (this is non-deterministic, so we'll ignore matching by it)
        encrypted_token: str = encrypt_token(token)
        current_time: datetime = datetime.now(timezone.utc)

        result = await session.execute(
            select(Credentials).where(Credentials.credential_key == "github_pat")
        )
        credential: Optional[Credentials] = result.scalars().first()

        if credential is not None:
            raise HTTPException(
                status_code=409,
                detail="Token already ingested. Use update-token to update it.",
            )

        credential = Credentials(
            credential_key="github_pat",
            token_hash=encrypted_token, 
            created_at=current_time
        )
        session.add(credential)

        # Set the isTokenSubmitted flag to true
        flag_result = await session.execute(
            select(Flag).where(Flag.name == "isTokenSubmitted")
        )  # type: ignore
        token_flag: Optional[Flag] = flag_result.scalar_one_or_none()

        if token_flag is None:
            # Create the flag if it doesn't exist
            token_flag = Flag(name="isTokenSubmitted", status=True)
        else:
            # Update existing flag
            token_flag.status = True

        session.add(token_flag)

        return {"message": "Token ingested successfully."}
    except HTTPException:
        # Re-raise HTTP exceptions (like 409) without modification
        raise
    except Exception as e:
        logger.error("Failed to process token: {}", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to process authentication token"
        )


@app.put("/update-token", status_code=200)
async def update_token(
    authorization: str = Header(...), session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token: str = authorization[7:].strip()
    try:
        encrypted_token: str = encrypt_token(token)
        current_time: datetime = datetime.now(timezone.utc)

        result = await session.execute(
            select(Credentials).where(Credentials.credential_key == "github_pat")
        )
        credential: Optional[Credentials] = result.scalars().first()
        if credential is None:
            raise HTTPException(status_code=404, detail="No GitHub token found to update")

        credential.token_hash = encrypted_token
        credential.updated_at = current_time
        session.add(credential)

        return {"message": "Token updated successfully."}
    except Exception as e:
        logger.error("Failed to update token: {}", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to update authentication token"
        )


@app.delete("/delete-token", status_code=200)
async def delete_token(session: AsyncSession = Depends(get_session)) -> Dict[str, str]:
    try:
        # Find existing credential
        result = await session.execute(
            select(Credentials).where(Credentials.credential_key == "github_pat")
        )
        credential: Optional[Credentials] = result.scalars().first()
        if credential is None:
            raise HTTPException(status_code=404, detail="No GitHub token found to delete")

        await session.delete(credential)

        # Set the isTokenSubmitted flag to false
        flag_result = await session.execute(
            select(Flag).where(Flag.name == "isTokenSubmitted")
        )
        token_flag: Optional[Flag] = flag_result.scalar_one_or_none()

        if token_flag is None:
            # Create the flag if it doesn't exist
            token_flag = Flag(name="isTokenSubmitted", status=False)
        else:
            # Update existing flag
            token_flag.status = False

        session.add(token_flag)

        return {"message": "Token deleted successfully."}
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions directly
        raise http_ex
    except Exception as e:
        logger.error("Failed to delete token: {}", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to delete authentication token"
        )


@app.get("/repos", response_model=PaginatedResponse)
async def get_repos(
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    filterValues: Optional[str] = Query(
        None, description="Optional JSON filter values to filter repositories"
    ),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse:
    # Fetch GitHub token from database using helper function
    token = await fetch_github_token_from_db(session)

    # Parse filterValues if provided, and merge with the search parameter
    filter_values_dict: dict = {}
    if filterValues:
        try:
            filter_values_dict = json.loads(filterValues)
        except Exception as e:
            logger.error("Invalid JSON in filterValues: {}", e)
            raise HTTPException(
                status_code=400, detail="Invalid JSON in filterValues query parameter"
            )
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
                "User-Agent": "Unoplat Code Confluence",
            },
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
                result = await client.execute(
                    query,
                    variable_values={
                        "query": search_query,
                        "first": per_page,
                        "after": cursor,
                    },
                )

                # Process the search result
                repos_data = result["search"]["nodes"]  # type: ignore
                has_next = result["search"]["pageInfo"]["hasNextPage"]  # type: ignore
                next_cursor = result["search"]["pageInfo"]["endCursor"]  # type: ignore
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
                result = await client.execute(
                    query, variable_values={"first": per_page, "after": cursor}
                )

                # Process the result
                repos_data = result["viewer"]["repositories"]["nodes"]  # type: ignore
                has_next = result["viewer"]["repositories"]["pageInfo"]["hasNextPage"]  # type: ignore
                next_cursor = result["viewer"]["repositories"]["pageInfo"]["endCursor"]  # type: ignore

            # Convert to GitHubRepoSummary objects
            repos_list: List[GitHubRepoSummary] = []
            for item in repos_data:
                repo_summary = GitHubRepoSummary(
                    name=item["name"],
                    owner_url=item["owner"]["url"],
                    private=item["isPrivate"],
                    git_url=item["url"],
                    owner_name=item["owner"]["login"],
                )
                repos_list.append(repo_summary)

            # Return paginated response with cursor as metadata
            return PaginatedResponse(
                items=repos_list,
                per_page=per_page,
                has_next=has_next,
                next_cursor=next_cursor,
            )

    except Exception as e:
        logger.error("GraphQL Error: {}", str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch repositories: {str(e)}"
        )


@app.post("/start-ingestion", status_code=201)
async def ingestion(
    repo_request: GitHubRepoRequestConfiguration,
    session: AsyncSession = Depends(get_session),
    request_logger: "Logger" = Depends(trace_dependency),  # type: ignore
) -> dict[str, str]:
    """
    Start the ingestion workflow for the entire repository using the GitHub token from the database.
    Submits the whole repo_request at once to the Temporal workflow.
    Returns the workflow_id and run_id.
    Also ingests the repository configuration into the database.
    """
    # Handle local repository path construction based on environment
    if repo_request.is_local and repo_request.local_path:
        # For local repositories, construct the full path based on runtime environment
        # local_path contains just the folder name (e.g., "dspy")
        folder_name = repo_request.local_path
        actual_path = construct_local_repository_path(folder_name)
        # Update the local_path field with the constructed full path
        repo_request.local_path = actual_path
        request_logger.info(
            "Local repository ingestion - folder: {}, resolved path: {}, environment: {}",
            folder_name,
            actual_path,
            get_runtime_environment(),
        )

        # Extract actual GitHub organization from git remote origin for consistent qualified name generation
        # This ensures PostgreSQL and Neo4j use the same organization name instead of "local"
        original_owner = repo_request.repository_owner_name
        github_organization = extract_github_organization_from_local_repo(
            actual_path, original_owner
        )
        repo_request.repository_owner_name = github_organization
        request_logger.info(
            "Local repository GitHub organization - original: {}, extracted: {}",
            original_owner,
            github_organization,
        )

        # Rebuild trace_id with the updated organization to ensure workflow ID consistency
        updated_trace_id = build_trace_id(
            repo_request.repository_name, github_organization
        )
        trace_id_var.set(updated_trace_id)
        request_logger.info(
            "Updated trace_id for workflow consistency - new: {}", updated_trace_id
        )

    # Fetch GitHub token from database for remote repositories (not needed for local)
    if not repo_request.is_local:
        github_token = await fetch_github_token_from_db(session)
    else:
        github_token = ""

    # Fetch the trace-id (now potentially updated for local repos)
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

    request_logger.info(
        "Started workflow. Workflow ID: {}, RunID {}",
        workflow_handle.id,
        workflow_handle.result_run_id,
    )
    return {"workflow_id": workflow_handle.id or "none", "run_id": run_id}


@app.get("/flags/{flag_name}", status_code=200)
async def get_flag_status(
    flag_name: str, session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
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
        return {"name": flag.name, "status": flag.status, "exists": True}
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions directly
        raise http_ex
    except Exception as e:
        logger.error("Failed to get flag status: {}", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to get flag status for {}".format(flag_name)
        )


@app.get("/flags", status_code=200)
async def get_all_flags(
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
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
        return [{"name": flag.name, "status": flag.status} for flag in flags]
    except Exception as e:
        logger.error("Failed to get flags: {}", str(e))
        raise HTTPException(status_code=500, detail="Failed to get flags")


@app.put("/flags/{flag_name}", status_code=200)
async def set_flag_status(
    flag_name: str, status: bool, session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
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

        return {"name": flag.name, "status": flag.status}
    except Exception as e:
        logger.error("Failed to set flag status: {}", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to set flag status for {}".format(flag_name)
        )


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


@app.get(
    "/repository-status",
    response_model=GithubRepoStatus,
)
async def get_repository_status(
    repository_name: str = Query(..., description="The name of the repository"),
    repository_owner_name: str = Query(
        ..., description="The name of the repository owner"
    ),
    workflow_run_id: str = Query(
        ..., description="The workflow run ID to fetch status for"
    ),
    session: AsyncSession = Depends(get_session),
) -> GithubRepoStatus:
    """
    Get the current status of a repository workflow run and its associated codebase runs.
    """
    try:
        # Build base query for repository workflow run
        stmt = select(RepositoryWorkflowRun).where(
            RepositoryWorkflowRun.repository_name == repository_name,
            RepositoryWorkflowRun.repository_owner_name == repository_owner_name,
            RepositoryWorkflowRun.repository_workflow_run_id == workflow_run_id,
        )

        parent_run = (await session.execute(stmt)).scalar_one_or_none()
        if not parent_run:
            error_msg = "Workflow run {} not found for {}/{}".format(
                workflow_run_id, repository_name, repository_owner_name
            )
            raise HTTPException(status_code=404, detail=error_msg)

        # Fetch all codebase workflow runs associated with this parent run
        cb_stmt = select(CodebaseWorkflowRun).where(
            CodebaseWorkflowRun.repository_name == repository_name,
            CodebaseWorkflowRun.repository_owner_name == repository_owner_name,
            CodebaseWorkflowRun.repository_workflow_run_id
            == parent_run.repository_workflow_run_id,
        )
        codebase_runs = (await session.execute(cb_stmt)).scalars().all()

        # Group codebase runs by codebase_folder
        codebase_data: Dict[str, List[Tuple[str, WorkflowRun]]] = {}
        for run in codebase_runs:
            codebase_folder = run.codebase_folder
            if codebase_folder not in codebase_data:
                codebase_data[codebase_folder] = []

            error_report = ErrorReport(**run.error_report) if run.error_report else None

            # Create WorkflowRun object for this codebase run
            workflow_run = WorkflowRun(
                codebase_workflow_run_id=run.codebase_workflow_run_id,
                status=JobStatus(run.status),
                started_at=run.started_at,
                completed_at=run.completed_at,
                error_report=error_report,
                issue_tracking=IssueTracking(**run.issue_tracking)
                if run.issue_tracking
                else None,
            )

            # Add to the list of runs for this codebase
            codebase_data[codebase_folder].append(
                (run.codebase_workflow_id, workflow_run)
            )

        # Now organize workflow runs by workflow ID
        codebases: List[CodebaseStatus] = []
        for codebase_folder, runs in codebase_data.items():
            # Group workflow runs by workflow ID
            workflow_map: Dict[str, List[WorkflowRun]] = {}
            for workflow_id, wf_run in runs:
                if workflow_id not in workflow_map:
                    workflow_map[workflow_id] = []
                workflow_map[workflow_id].append(wf_run)

            # Create WorkflowStatus objects for each workflow ID
            workflows: List[WorkflowStatus] = []
            for workflow_id, workflow_runs in workflow_map.items():
                workflows.append(
                    WorkflowStatus(
                        codebase_workflow_id=workflow_id,
                        codebase_workflow_runs=workflow_runs,
                    )
                )

            # Create CodebaseStatus for this codebase
            codebases.append(
                CodebaseStatus(codebase_folder=codebase_folder, workflows=workflows)
            )

        # Create CodebaseStatusList with all codebase statuses
        codebase_status_list: Optional[CodebaseStatusList] = (
            CodebaseStatusList(codebases=codebases) if codebases else None
        )

        # Create parent repository status object
        return GithubRepoStatus(
            repository_name=parent_run.repository_name,
            repository_owner_name=parent_run.repository_owner_name,
            repository_workflow_run_id=parent_run.repository_workflow_run_id,
            repository_workflow_id=parent_run.repository_workflow_id,
            issue_tracking=IssueTracking(**parent_run.issue_tracking)
            if parent_run.issue_tracking
            else None,
            status=JobStatus(parent_run.status),
            started_at=parent_run.started_at,
            completed_at=parent_run.completed_at,
            error_report=ErrorReport(**parent_run.error_report)
            if parent_run.error_report
            else None,
            codebase_status_list=codebase_status_list,
        )
    except Exception as e:
        logger.error("Error retrieving repository status: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error retrieving repository status: {}".format(str(e)),
        )


@app.get(
    "/repository-data",
    response_model=GitHubRepoResponseConfiguration,
)
async def get_repository_data(
    repository_name: str = Query(..., description="The name of the repository"),
    repository_owner_name: str = Query(
        ..., description="The name of the repository owner"
    ),
    session: AsyncSession = Depends(get_session),
) -> GitHubRepoResponseConfiguration:
    # fetch repository record with its codebase configs
    db_obj: Repository | None = await session.get(
        Repository,
        (repository_name, repository_owner_name),
        options=[selectinload(cast(QueryableAttribute[Any], Repository.configs))],
    )
    if not db_obj:
        raise HTTPException(
            status_code=404,
            detail="Repository data not found for {}/{}".format(
                repository_name, repository_owner_name
            ),
        )

    # Map database CodebaseConfig entries to Pydantic models
    try:
        codebases = [
            CodebaseConfig(
                codebase_folder=config.codebase_folder,
                root_packages=config.root_packages,
                programming_language_metadata=ProgrammingLanguageMetadata(
                    language=config.programming_language_metadata["language"],
                    package_manager=config.programming_language_metadata[
                        "package_manager"
                    ],
                    language_version=config.programming_language_metadata.get(
                        "language_version"
                    ),
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
        logger.error("Error mapping repository data: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error processing repository data for {}/{}".format(
                repository_name, repository_owner_name
            ),
        )


@app.get(
    "/parent-workflow-jobs",
    response_model=ParentWorkflowJobListResponse,
    description="Get all parent workflow jobs data without pagination",
)
async def get_parent_workflow_jobs(
    session: AsyncSession = Depends(get_session),
) -> ParentWorkflowJobListResponse:
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
                completed_at=run.completed_at,
            )
            for run in workflow_runs
        ]

        return ParentWorkflowJobListResponse(jobs=jobs)
    except Exception as e:
        logger.error("Error retrieving parent workflow jobs: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error retrieving parent workflow jobs: {}".format(str(e)),
        )


@app.get(
    "/get/ingestedRepositories",
    response_model=IngestedRepositoriesListResponse,
    description="Get all ingested repositories without pagination",
)
async def get_ingested_repositories(
    session: AsyncSession = Depends(get_session),
) -> IngestedRepositoriesListResponse:
    """Get all ingested repositories without pagination.

    Returns basic information for all repositories in the database.
    Includes repository_name and repository_owner_name only.
    """
    try:
        # Query to get all repositories
        query = select(Repository)
        result = await session.execute(query)
        repositories = result.scalars().all()

        # Transform the database records to the response model format
        repo_list = [
            IngestedRepositoryResponse(
                repository_name=repo.repository_name,
                repository_owner_name=repo.repository_owner_name,
                is_local=repo.is_local,
                local_path=repo.local_path,
            )
            for repo in repositories
        ]

        return IngestedRepositoriesListResponse(repositories=repo_list)
    except Exception as e:
        logger.error("Error retrieving ingested repositories: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error retrieving ingested repositories: {}".format(str(e)),
        )


@app.delete("/delete-repository", status_code=200)
async def delete_repository(
    repo_info: IngestedRepositoryResponse, session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Delete a repository from both PostgreSQL and Neo4j databases.

    This endpoint removes a repository and all its associated data including:
    - Repository record and cascaded relations in PostgreSQL
    - Repository node and all connected nodes/relationships in Neo4j

    Args:
        repo_info: IngestedRepositoryResponse containing repository_name and repository_owner_name
        session: Database session

    Returns:
        Success message with deletion statistics

    Raises:
        HTTPException: 404 if repository not found, 500 on error
    """
    repository_name = repo_info.repository_name
    repository_owner_name = repo_info.repository_owner_name

    try:
        # First check if repository exists in PostgreSQL
        db_obj: Repository | None = await session.get(
            Repository, (repository_name, repository_owner_name)
        )
        if not db_obj:
            raise HTTPException(
                status_code=404,
                detail="Repository not found: {}/{}".format(
                    repository_owner_name, repository_name
                ),
            )

        # Delete from PostgreSQL - cascade will handle related tables
        await session.delete(db_obj)
        await session.commit()

        logger.info(
            "Deleted repository from PostgreSQL: {}/{}",
            repository_owner_name,
            repository_name,
        )

        # Delete from Neo4j using qualified name format
        qualified_name = "{}_{}".format(repository_owner_name, repository_name)

        try:
            async with app.state.code_confluence_graph.get_session() as neo4j_session:
                neo4j_stats = await app.state.code_confluence_graph_deletion.delete_repository_by_qualified_name_managed(
                    session=neo4j_session, qualified_name=qualified_name
                )
            logger.info("Deleted repository from Neo4j: {}", qualified_name)
        except ApplicationError as neo4j_error:
            # Log Neo4j error but don't fail if already deleted
            if neo4j_error.type == "REPOSITORY_NOT_FOUND":
                logger.warning(
                    "Repository not found in Neo4j (may have been already deleted): {}",
                    qualified_name,
                )
                neo4j_stats = {
                    "repository_qualified_name": qualified_name,
                    "status": "not_found",
                }
            else:
                # For other errors, re-raise
                raise neo4j_error

        return {
            "message": "Successfully deleted repository {}/{}".format(
                repository_owner_name, repository_name
            ),
            "repository_name": repository_name,
            "repository_owner_name": repository_owner_name,
            "neo4j_deletion_stats": neo4j_stats,
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ApplicationError as e:
        # Handle Neo4j application errors
        logger.error("Neo4j deletion error: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to delete repository from graph database: {}".format(str(e)),
        )
    except Exception as e:
        logger.error("Error deleting repository: {}", str(e))
        raise HTTPException(
            status_code=500, detail="Error deleting repository: {}".format(str(e))
        )


@app.post(
    "/refresh-repository", response_model=RefreshRepositoryResponse, status_code=201
)
async def refresh_repository(
    repo_info: IngestedRepositoryResponse,
    session: AsyncSession = Depends(get_session),
    request_logger: "Logger" = Depends(trace_dependency),  # type: ignore
) -> RefreshRepositoryResponse:
    """
    Refresh a repository by purging Neo4j data and re-ingesting.

    This endpoint:
    1. Deletes all repository data from Neo4j (keeps PostgreSQL intact)
    2. Re-detects codebases using PythonCodebaseDetector
    3. Starts a new Temporal workflow for ingestion

    Args:
        repo_info: Repository name and owner
        session: Database session
        request_logger: Logger with trace ID

    Returns:
        RefreshRepositoryResponse with workflow IDs
    """
    repository_name: str = repo_info.repository_name
    repository_owner_name: str = repo_info.repository_owner_name

    try:
        # 1. Get repository info from database to determine if it's local or remote
        db_repo: Repository | None = await session.get(
            Repository, (repository_name, repository_owner_name)
        )
        if not db_repo:
            raise HTTPException(
                status_code=404,
                detail="Repository not found in database: {}/{}".format(
                    repository_name, repository_owner_name
                ),
            )

        # Use database values for local repository information
        is_local = db_repo.is_local
        local_path = db_repo.local_path

        # 2. Delete from Neo4j (reuse existing pattern from delete-repository)
        qualified_name: str = "{}_{}".format(repository_owner_name, repository_name)

        try:
            async with app.state.code_confluence_graph.get_session() as neo4j_session:
                await app.state.code_confluence_graph_deletion.delete_repository_by_qualified_name_managed(
                    session=neo4j_session, qualified_name=qualified_name
                )
            request_logger.info("Deleted repository from Neo4j: {}", qualified_name)
        except ApplicationError as neo4j_error:
            # Log but don't fail if already deleted
            if neo4j_error.type == "REPOSITORY_NOT_FOUND":
                request_logger.warning(
                    "Repository not found in Neo4j: {}", qualified_name
                )
            else:
                raise HTTPException(
                    status_code=500, detail=f"Neo4j deletion failed: {str(neo4j_error)}"
                )

        # 3. Fetch GitHub token only for remote repositories
        github_token: str = ""
        if not is_local:
            github_token = await fetch_github_token_from_db(session)

        # 4. Handle repository path/URL based on type
        if is_local:
            if not local_path:
                raise HTTPException(
                    status_code=400, detail="local_path required for local repositories"
                )

            # Check if local_path is already absolute or just a folder name
            if os.path.isabs(local_path):
                # Already absolute path, use directly
                actual_local_path = local_path
                # For validation, extract just the folder name from the absolute path
                folder_name_for_validation = os.path.basename(local_path)
            else:
                # Just folder name, construct full path using environment utils
                actual_local_path = construct_local_repository_path(local_path)
                folder_name_for_validation = local_path

            # Validate local repository exists
            is_valid, validated_path = validate_local_repository_path(
                folder_name_for_validation
            )
            if not is_valid:
                raise HTTPException(
                    status_code=404,
                    detail=f"Local repository not found: {validated_path}",
                )

            repository_url = f"file://{actual_local_path}"
            request_logger.info("Refreshing local repository: {}", actual_local_path)
        else:
            repository_url = (
                f"https://github.com/{repository_owner_name}/{repository_name}"
            )
            actual_local_path = None
            request_logger.info("Refreshing GitHub repository: {}", repository_url)

        # 5. Detect codebases using shared ripgrep detector instance
        detector: PythonRipgrepDetector = app.state.python_codebase_detector
        detected_codebases: List[CodebaseConfig]
        try:
            if is_local:
                # Use actual local path for detection
                detected_codebases = await detector.detect_codebases(
                    actual_local_path, github_token=github_token
                )  # type: ignore
            else:
                # Use GitHub URL for detection with github_token
                detected_codebases = await detector.detect_codebases(
                    repository_url, github_token=github_token
                )

            request_logger.info(
                "Detected {} codebases for {}/{}",
                len(detected_codebases),
                repository_owner_name,
                repository_name,
            )
        except Exception as e:
            request_logger.error("Codebase detection failed: {}", str(e))
            raise HTTPException(
                status_code=500, detail=f"Failed to detect codebases: {str(e)}"
            )

        # 6. Build repository request configuration with local support
        repo_request: GitHubRepoRequestConfiguration = GitHubRepoRequestConfiguration(
            repository_name=repository_name,
            repository_owner_name=repository_owner_name,
            repository_git_url=repository_url,
            repository_metadata=detected_codebases,
            is_local=is_local,
            local_path=actual_local_path if is_local else None,
        )

        # 7. Start Temporal workflow
        trace_id: Optional[str] = trace_id_var.get()
        if not trace_id:
            raise HTTPException(500, "trace_id not set by dependency")

        workflow_handle: WorkflowHandle = await start_workflow(
            temporal_client=app.state.temporal_client,
            repo_request=repo_request,
            github_token=github_token,
            workflow_id=f"refresh-{repository_owner_name}-{repository_name}-{trace_id}",
            trace_id=trace_id,
        )

        # 8. Schedule background monitoring
        asyncio.create_task(monitor_workflow(workflow_handle))

        request_logger.info(
            f"Started refresh workflow for {repository_owner_name}/{repository_name}. "
            f"Workflow ID: {workflow_handle.id}, RunID: {workflow_handle.result_run_id}"
        )

        return RefreshRepositoryResponse(
            repository_name=repository_name,
            repository_owner_name=repository_owner_name,
            workflow_id=workflow_handle.id or "",
            run_id=workflow_handle.result_run_id or "",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        request_logger.error("Error refreshing repository: {}", str(e))
        raise HTTPException(
            status_code=500, detail=f"Error refreshing repository: {str(e)}"
        )


@app.get("/user-details", status_code=200)
async def get_user_details(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Optional[str]]:
    """
    Fetch authenticated GitHub user's name, avatar URL, and email.
    """
    # Fetch GitHub token from database using helper function
    token = await fetch_github_token_from_db(session)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient() as client:
        # Primary user info
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=user_resp.status_code, detail="Failed to fetch user info"
            )
        user_data = user_resp.json()

        # Determine email: use public email or fetch primary email via separate endpoint
        email = user_data.get("email")

        if not email:
            emails_resp = await client.get(
                "https://api.github.com/user/emails", headers=headers
            )
            if emails_resp.status_code == 200:
                emails = emails_resp.json()
                primary = next(
                    (
                        e["email"]
                        for e in emails
                        if e.get("primary") and e.get("verified")
                    ),
                    None,
                )
                email = primary

    return {
        "name": user_data.get("name"),
        "avatar_url": user_data.get("avatar_url"),
        "email": email,
    }


@app.get("/detect-codebases-sse")
async def detect_codebases_sse_endpoint(
    git_url: str = Query(
        ..., description="GitHub repository URL or folder name for local repository"
    ),
    is_local: bool = Query(False, description="Whether this is a local repository"),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """
    Server-Sent Events endpoint for real-time codebase detection progress (v2).

    This version directly uses PythonCodebaseDetector without the AsyncDetectorWrapper.
    Streams progress updates during Python codebase auto-detection from GitHub repositories
    or local Git repositories.

    Args:
        git_url: GitHub repository URL or folder name for local repository
        is_local: Whether this is a local repository
        session: Database session for token retrieval

    Returns:
        StreamingResponse with text/event-stream content type
    """
    return await detect_codebases_sse(git_url, is_local, session)


@app.post("/code-confluence/issues", response_model=IssueTracking)
async def create_github_issue(
    request: GithubIssueSubmissionRequest, session: AsyncSession = Depends(get_session)
) -> IssueTracking:
    """
    Create a GitHub issue based on error information and track it in the database.

    This endpoint creates a GitHub issue using the provided error information and then updates
    either the codebase workflow run or repository workflow run record with the issue details.
    """
    try:
        # Get GitHub token from credentials using helper function
        token = await fetch_github_token_from_db(session)

        # Create GitHub issue

        # Create issue title and body from error information
        title = (
            f"Error: {request.error_message_body[:50]}..."
            if len(request.error_message_body) > 50
            else f"Error: {request.error_message_body}"
        )
        body = f"## Error Details\n\n{request.error_message_body}\n\n"

        # Add workflow context information to the issue body
        body += "## Workflow Information\n\n"
        body += (
            f"- Repository: {request.repository_owner_name}/{request.repository_name}\n"
        )

        if request.codebase_folder:
            body += f"- Codebase Folder: {request.codebase_folder}\n"

        # Build the GitHub API request data
        github_issue_data = {
            "title": title,
            "body": body,
            # Assignees and labels could be added here if needed
            # "assignees": [],
            "labels": ["bug", "automated"],
        }

        # Create GitHub issue using PyGithub
        try:
            # Initialize GitHub client with token
            g = Github(token)

            # Get the repository
            repo = g.get_repo("unoplat/unoplat-code-confluence")

            # Create the issue
            labels = github_issue_data["labels"]
            github_issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels,  # type: ignore
            )
        except Exception as e:
            logger.error("GitHub API error: {}", str(e))
            raise HTTPException(
                status_code=500, detail=f"Failed to create GitHub issue: {str(e)}"
            )

        # Create issue tracking record
        issue_tracking = IssueTracking(
            issue_id=str(github_issue.id),
            issue_url=github_issue.html_url,
            issue_status=IssueStatus.OPEN,
        )

        # Prepare issue tracking data for database using IssueTracking model
        issue_tracking_full = IssueTracking(
            issue_id=issue_tracking.issue_id,
            issue_number=github_issue.number,
            issue_url=issue_tracking.issue_url,
            issue_status=issue_tracking.issue_status,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        issue_data = (
            issue_tracking_full.model_dump()
        )  # or use .json() if the DB expects a JSON string

        # Save to appropriate table based on issue type
        if (
            request.error_type == IssueType.CODEBASE
            and request.codebase_workflow_run_id
        ):
            # Update codebase workflow run with issue tracking
            condition = (
                (CodebaseWorkflowRun.repository_name == request.repository_name)
                & (
                    CodebaseWorkflowRun.repository_owner_name
                    == request.repository_owner_name
                )
                & (CodebaseWorkflowRun.codebase_folder == request.codebase_folder)
                & (
                    CodebaseWorkflowRun.codebase_workflow_run_id
                    == request.codebase_workflow_run_id
                )
            )  # type: ignore
            codebase_run_query = select(CodebaseWorkflowRun).where(condition)
            codebase_run_result = await session.execute(codebase_run_query)
            codebase_run = codebase_run_result.scalar_one_or_none()

            if not codebase_run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Codebase workflow run {request.codebase_workflow_run_id} not found",
                )

            codebase_run.issue_tracking = issue_data

        else:  # repository workflow run
            # Update repository workflow run with issue tracking
            condition = (
                (RepositoryWorkflowRun.repository_name == request.repository_name)
                & (
                    RepositoryWorkflowRun.repository_owner_name
                    == request.repository_owner_name
                )
                & (
                    RepositoryWorkflowRun.repository_workflow_run_id
                    == request.parent_workflow_run_id
                )
            )  # type: ignore
            repo_run_query = select(RepositoryWorkflowRun).where(condition)
            repo_run_result = await session.execute(repo_run_query)
            repo_run = repo_run_result.scalar_one_or_none()

            if not repo_run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Repository workflow run {request.parent_workflow_run_id} not found",
                )

            repo_run.issue_tracking = issue_data

        return issue_tracking_full

    except Exception as e:
        logger.error("Error creating GitHub issue: {}", str(e))
        # Follow standardized error handling pattern from memories
        workflow_context = {
            "workflow_id": request.parent_workflow_run_id,
            "repository": f"{request.repository_owner_name}/{request.repository_name}",
        }
        if (
            request.error_type == IssueType.CODEBASE
            and request.codebase_workflow_run_id
        ):
            workflow_context["codebase_workflow_run_id"] = (
                request.codebase_workflow_run_id
            )
            if request.codebase_folder:
                workflow_context["codebase_folder"] = request.codebase_folder

        error_context = {
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "workflow_context": workflow_context,
        }

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Faced an error while creating GitHub issue. Please try after some time.",
                "error_context": error_context,
            },
        )


