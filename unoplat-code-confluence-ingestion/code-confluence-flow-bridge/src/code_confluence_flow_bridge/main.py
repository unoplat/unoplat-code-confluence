import os
import asyncio
from collections.abc import AsyncGenerator, Callable
from concurrent.futures import ThreadPoolExecutor
import traceback

from fastapi import Depends, FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.client import Client, WorkflowHandle
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import ApplicationError
from temporalio.worker import PollerBehaviorAutoscaling, Worker
from unoplat_code_confluence_commons.base_models import (
    Repository,
)
from unoplat_code_confluence_commons.credential_enums import CredentialNamespace

from src.code_confluence_flow_bridge.github_app.router import (
    router as github_app_router,
)
from src.code_confluence_flow_bridge.logging.log_config import setup_logging
from src.code_confluence_flow_bridge.logging.logger_protocol import StructuredLogger
from src.code_confluence_flow_bridge.logging.trace_utils import (
    trace_id_var,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.models.github.github_repo import (
    RepositoryRequestConfiguration,
)
from src.code_confluence_flow_bridge.parser.package_manager.python.detectors.ripgrep_detector import (
    PythonRipgrepDetector,
)
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.ripgrep_detector import (
    TypeScriptRipgrepDetector,
)
from src.code_confluence_flow_bridge.processor.activity_inbound_interceptor import (
    ActivityStatusInterceptor,
)
from src.code_confluence_flow_bridge.processor.codebase_child_workflow import (
    CodebaseChildWorkflow,
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
from src.code_confluence_flow_bridge.routers.credentials.router import (
    router as credentials_router,
)
from src.code_confluence_flow_bridge.routers.flags.router import (
    router as flags_router,
)
from src.code_confluence_flow_bridge.routers.github_issues.router import (
    router as github_issues_router,
)
from src.code_confluence_flow_bridge.routers.operations.router import (
    router as operations_router,
)
from src.code_confluence_flow_bridge.routers.providers.router import (
    router as providers_router,
)
from src.code_confluence_flow_bridge.routers.repository.router import (
    router as repository_router,
)
from src.code_confluence_flow_bridge.utility.deps import trace_dependency
from src.code_confluence_flow_bridge.utility.detection import (
    CodebaseDetector,
    detect_codebases_multi_language,
)
from src.code_confluence_flow_bridge.utility.runtime_deps import (
    get_codebase_detectors,
    get_temporal_client_dep,
)
from src.code_confluence_flow_bridge.utility.token_utils import (
    fetch_repository_provider_token,
)
from src.code_confluence_flow_bridge.utility.workflow_helpers import (
    monitor_workflow,
    start_workflow,
)

# Setup logging - override imported logger with configured one
logger = setup_logging(
    service_name="code-confluence-flow-bridge", app_name="unoplat-code-confluence"
)

ActivityCallable = Callable[..., object]


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
    activities: list[ActivityCallable],
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
        # Configure poller behaviors based on settings
        if env_settings.temporal_enable_poller_autoscaling:
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


# Create FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.code_confluence_env = EnvironmentSettings()
    logger.info(
        "Starting code-confluence-flow-bridge service with PostgreSQL storage backend"
    )
    app.state.temporal_client = await get_temporal_client()

    # Initialize shared PythonRipgrepDetector instance
    app.state.python_codebase_detector = PythonRipgrepDetector()
    await app.state.python_codebase_detector.initialize_rules()
    logger.info("PythonRipgrepDetector initialized successfully")

    # Initialize shared TypeScript detector instance
    app.state.typescript_codebase_detector = TypeScriptRipgrepDetector()
    await app.state.typescript_codebase_detector.initialize_rules()
    logger.info("TypeScriptRipgrepDetector initialized successfully")

    # Fast lookup for detectors by language key
    app.state.codebase_detectors = {
        "python": app.state.python_codebase_detector,
        "typescript": app.state.typescript_codebase_detector,
    }

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
    git_activity = GitActivity()
    parent_workflow_db_activity: ParentWorkflowDbActivity = ParentWorkflowDbActivity()
    child_workflow_db_activity = ChildWorkflowDbActivity()
    package_metadata_activity = PackageMetadataActivity()
    confluence_git_graph = ConfluenceGitGraph()
    codebase_package_ingestion = PackageManagerMetadataIngestion()
    generic_activity = GenericCodebaseProcessingActivity()
    activities: list[ActivityCallable] = [
        git_activity.process_git_activity,
        parent_workflow_db_activity.update_repository_workflow_status,
        child_workflow_db_activity.update_codebase_workflow_status,
        package_metadata_activity.get_package_metadata,
        confluence_git_graph.insert_git_repo_into_graph_db,
        codebase_package_ingestion.insert_package_manager_metadata,
        generic_activity.process_codebase_generic,
    ]

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

        # 4. Dispose SQLAlchemy async engine
        try:
            await dispose_current_engine()
            logger.info("SQLAlchemy engine disposed")
        except Exception as exc:
            logger.warning("Failed to dispose async engine during shutdown: {}", exc)

        # 5. Shut down the thread pool executor (after worker is done)
        try:
            app.state.activity_executor.shutdown(wait=True)
            logger.info("Thread pool executor shut down")
        except Exception as e:
            logger.error("Error shutting down thread pool executor: {}", e)


app = FastAPI(lifespan=lifespan)

# Configure CORS
origins: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(github_app_router)
app.include_router(github_issues_router)
app.include_router(credentials_router)
app.include_router(flags_router)
app.include_router(providers_router)
app.include_router(repository_router)
app.include_router(operations_router)


@app.post("/start-ingestion", status_code=201)
async def ingestion(
    repo_request: RepositoryRequestConfiguration,
    session: AsyncSession = Depends(get_session),
    request_logger: StructuredLogger = Depends(trace_dependency),
    temporal_client: Client = Depends(get_temporal_client_dep),
    detectors: dict[str, CodebaseDetector] = Depends(get_codebase_detectors),
) -> dict[str, str]:
    """
    Start the ingestion workflow for the entire repository using the repository provider token from the database.
    Submits the whole repo_request at once to the Temporal workflow.
    Returns the workflow_id and run_id.
    Also ingests the repository configuration into the database.
    """
    # Check for existing repository — prevent duplicate ingestion
    existing_repo: Repository | None = await session.get(
        Repository, (repo_request.repository_name, repo_request.repository_owner_name)
    )
    if existing_repo is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Repository {repo_request.repository_owner_name}/{repo_request.repository_name} has already been ingested. Use Repository Operations to refresh or manage it.",
        )

    # Fetch repository provider token from database using provider_key from request
    github_token, _ = await fetch_repository_provider_token(
        session, CredentialNamespace.REPOSITORY, repo_request.provider_key
    )

    # AUTO-DETECT CODEBASES IF NOT PROVIDED
    if (
        repo_request.repository_metadata is None
        or len(repo_request.repository_metadata) == 0
    ):
        request_logger.info(
            "No codebases provided - starting auto-detection for {}/{}",
            repo_request.repository_owner_name,
            repo_request.repository_name,
        )

        # Run multi-language detection
        detected_codebases = await detect_codebases_multi_language(
            git_url=repo_request.repository_git_url,
            github_token=github_token,
            detectors=detectors,
            request_logger=request_logger,
        )

        repo_request.repository_metadata = detected_codebases
        request_logger.info(
            "Auto-detection completed - found {} codebases", len(detected_codebases)
        )
    else:
        request_logger.info(
            "Using provided codebases - count: {}",
            len(repo_request.repository_metadata),
        )

    # Fetch the trace-id (now potentially updated for local repos)
    trace_id = trace_id_var.get()
    if not trace_id:
        raise HTTPException(500, "trace_id not set by dependency")

    # Start the Temporal workflow
    workflow_handle: WorkflowHandle[
        RepoWorkflow, UnoplatGitRepository
    ] = await start_workflow(
        temporal_client=temporal_client,
        repo_request=repo_request,
        github_token=github_token,
        workflow_id=f"ingest-{repo_request.provider_key.value}-{trace_id}",
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
