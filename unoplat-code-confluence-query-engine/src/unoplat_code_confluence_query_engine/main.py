# Query engine entry point — serves the agent and API layer over ingested code graph data.
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase
from unoplat_code_confluence_commons.flags import Flag
import uvicorn

from unoplat_code_confluence_query_engine.api.v1.endpoints import (
    ai_model_config,
    app_feedback,
    codebase_agent_rules,
    flags,
    tool_config,
)
from unoplat_code_confluence_query_engine.config.logging_config import setup_logging
from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.db.postgres import db
from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.db.postgres.db import (
    dispose_db_connections,
    get_startup_session,
    init_db_connections,
)
from unoplat_code_confluence_query_engine.services.config.ai_model_config_service import (
    AiModelConfigService,
)
from unoplat_code_confluence_query_engine.services.config.codex_oauth_service import (
    CodexOAuthService,
)
from unoplat_code_confluence_query_engine.services.config.config_hot_reload import (
    register_orm_events,
    unregister_orm_events,
)
from unoplat_code_confluence_query_engine.services.flags.flag_service import FlagService
from unoplat_code_confluence_query_engine.services.mcp.mcp_server_manager import (
    MCPServerManager,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_worker_manager import (
    get_worker_manager,
)


async def _start_codex_callback_server(app: FastAPI) -> None:
    """Start lightweight callback listeners on configured callback hosts."""
    callback_port: int = app.state.settings.codex_openai_callback_port
    configured_hosts = app.state.settings.codex_openai_callback_hosts
    bind_addresses: list[tuple[str, str]] = []
    for host in (part.strip() for part in configured_hosts.split(",")):
        if not host:
            continue
        label = "IPv6" if ":" in host else "IPv4"
        bind_addresses.append((host, label))

    if not bind_addresses:
        bind_addresses = [("127.0.0.1", "IPv4"), ("::1", "IPv6")]

    servers: list[uvicorn.Server] = []
    tasks: list[asyncio.Task[None]] = []

    for host, label in bind_addresses:
        config = uvicorn.Config(
            app,
            host=host,
            port=callback_port,
            log_level="warning",
            access_log=False,
            lifespan="off",
        )
        server = uvicorn.Server(config)
        server.install_signal_handlers = lambda: None  # type: ignore[method-assign]
        task = asyncio.create_task(
            server.serve(),
            name=f"codex-oauth-callback-server-{label.lower()}",
        )

        await asyncio.sleep(0.2)
        if task.done():
            # Drain the task so Python doesn't emit
            # "Task exception was never retrieved".
            bind_exc: BaseException | None = None
            if not task.cancelled():
                bind_exc = task.exception()
            logger.warning(
                "Could not bind Codex OAuth callback listener on {} ({}) port {}: {}",
                host,
                label,
                callback_port,
                bind_exc or "task finished unexpectedly",
            )
        else:
            servers.append(server)
            tasks.append(task)
            logger.info(
                "Codex OAuth callback listener started on {}:{} ({})",
                host,
                callback_port,
                label,
            )

    app.state.codex_callback_servers = servers
    app.state.codex_callback_server_tasks = tasks
    app.state.codex_callback_server_ready = len(servers) > 0

    if not app.state.codex_callback_server_ready:
        logger.error(
            "Failed to start any Codex OAuth callback listener on port {}; "
            "port may be in use by another process",
            callback_port,
        )


async def _stop_codex_callback_server(app: FastAPI) -> None:
    """Stop all callback listeners if running."""
    servers: list[uvicorn.Server] = getattr(app.state, "codex_callback_servers", [])
    tasks: list[asyncio.Task[None]] = getattr(app.state, "codex_callback_server_tasks", [])
    app.state.codex_callback_server_ready = False
    if not servers:
        return
    for server in servers:
        server.should_exit = True
    for task in tasks:
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except TimeoutError:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    app.state.codex_callback_servers = []
    app.state.codex_callback_server_tasks = []
    logger.info("Codex OAuth callback listener(s) stopped")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan handler for startup and shutdown events."""
    # Startup
    app.state.settings = EnvironmentSettings()

    # Initialize logging system
    setup_logging(
        service_name="unoplat-code-confluence-query-engine",
        app_name="query-engine",
        log_level=app.state.settings.log_level,
    )

    # Initialize PostgreSQL connections
    await init_db_connections(app.state.settings)

    # Create database tables if they don't exist
    if db.async_engine is None:
        raise RuntimeError("PostgreSQL engine not initialized")

    async with db.async_engine.begin() as conn:
        await conn.run_sync(SQLBase.metadata.create_all)
        logger.info("Database tables created/verified")

    # Register ORM events for hot-reload
    register_orm_events()
    logger.info("ORM hot-reload events registered")

    # Initialize MCP Server Manager (configuration only - no server startup)
    # MCP servers are created on-demand by agent factories
    app.state.mcp_manager = MCPServerManager()
    await app.state.mcp_manager.load_config(app.state.settings.mcp_servers_config_path)

    # Context7-based library docs were removed in favor of Exa MCP.

    # Initialize services and store in app state
    app.state.ai_model_config_service = AiModelConfigService()
    app.state.codex_oauth_service = CodexOAuthService(app.state.settings)
    app.state.flag_service = FlagService()
    app.state.codex_callback_servers = []
    app.state.codex_callback_server_tasks = []
    app.state.codex_callback_server_ready = False
    logger.info("Services initialized and stored in app state")

    # Start dedicated callback listener for Codex OAuth redirect_uri parity.
    await _start_codex_callback_server(app)

    # Check if AI model configuration exists and update flag
    async with get_startup_session() as session:
        result = await session.execute(
            select(AiModelConfig).where(AiModelConfig.id == 1)
        )
        config = result.scalar_one_or_none()
        model_configured = config is not None

        if model_configured:
            logger.info(
                "AI model configured: {}/{}",
                config.provider_key,
                config.model_name,
            )
        else:
            logger.warning(
                "No AI model configuration found. "
                "Please configure via /ai-model-config endpoint."
            )

        # Ensure isModelConfigured flag reflects current state
        flag_result = await session.execute(
            select(Flag).where(Flag.name == "isModelConfigured")
        )
        flag = flag_result.scalar_one_or_none()
        if flag:
            flag.status = model_configured
        else:
            session.add(Flag(name="isModelConfigured", status=model_configured))

    # Start Temporal worker if enabled AND model is configured
    worker_manager = get_worker_manager()
    app.state.temporal_worker_manager = None

    if not app.state.settings.temporal_enabled:
        logger.info("Temporal worker disabled (TEMPORAL_ENABLED=false)")
    elif not model_configured:
        logger.info(
            "Temporal worker startup deferred: no AI model configured. "
            "Worker will start when model is configured via /ai-model-config."
        )
    else:
        try:
            await worker_manager.start(settings=app.state.settings)
            app.state.temporal_worker_manager = worker_manager
            logger.info(
                "Temporal worker started with build ID: {}",
                worker_manager.current_build_id,
            )
        except Exception as e:
            logger.error("Failed to start Temporal worker: {}", e)
            logger.warning("Agent endpoints will return 503 Service Unavailable")

    yield

    # Shutdown
    # Stop Temporal worker
    if app.state.temporal_worker_manager:
        try:
            await app.state.temporal_worker_manager.stop()
            logger.info("Temporal worker stopped")
        except Exception as e:
            logger.error("Error stopping Temporal worker: {}", e)

    try:
        await _stop_codex_callback_server(app)
    except Exception as e:
        logger.warning("Error stopping Codex callback listener: {}", e)

    # Unregister ORM events
    try:
        unregister_orm_events()
        logger.info("ORM events unregistered")
    except Exception as e:
        logger.warning("Error unregistering ORM events: {}", e)

    # MCP servers are now created on-demand by agent factories
    # Each agent manages its own MCP server lifecycle automatically
    # No explicit shutdown needed for MCP servers

    # Dispose PostgreSQL connections
    await dispose_db_connections()


app = FastAPI(lifespan=lifespan)

# Enhanced CORS middleware for SSE support (sse-starlette 3.0.2 compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Important for SSE headers
)

# Include API routers
app.include_router(codebase_agent_rules.router)
app.include_router(ai_model_config.router)
app.include_router(ai_model_config.callback_router)
app.include_router(flags.router)
app.include_router(tool_config.router)
app.include_router(app_feedback.router)
