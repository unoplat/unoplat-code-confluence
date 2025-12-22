from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase
from unoplat_code_confluence_commons.flags import Flag

from unoplat_code_confluence_query_engine.api.v1.endpoints import (
    ai_model_config,
    codebase_agent_rules,
    flags,
)
from unoplat_code_confluence_query_engine.config.logging_config import setup_logging
from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan handler for startup and shutdown events."""
    # Startup
    app.state.settings = EnvironmentSettings()

    # Initialize logging system
    setup_logging(app.state.settings)

    # Initialize PostgreSQL connections
    await init_db_connections(app.state.settings)

    # Create database tables if they don't exist
    async with db.async_engine.begin() as conn:
        await conn.run_sync(SQLBase.metadata.create_all)
        logger.info("Database tables created/verified")

    # Register ORM events for hot-reload
    register_orm_events()
    logger.info("ORM hot-reload events registered")

    # Initialize Neo4j connection and store in app state
    app.state.neo4j_manager = CodeConfluenceGraphQueryEngine(app.state.settings)
    await app.state.neo4j_manager.connect()

    # Initialize MCP Server Manager (configuration only - no server startup)
    # MCP servers are created on-demand by agent factories
    app.state.mcp_manager = MCPServerManager()
    await app.state.mcp_manager.load_config(app.state.settings.mcp_servers_config_path)

    # Verify Context7 configuration is loaded
    if app.state.mcp_manager.has_server_config("context7"):
        logger.info("Context7 MCP server configuration loaded successfully")
    else:
        logger.warning(
            "Context7 MCP server configuration not found. "
            "Library documentation features will be unavailable."
        )

    # Initialize services and store in app state
    app.state.ai_model_config_service = AiModelConfigService()
    app.state.flag_service = FlagService()
    logger.info("Services initialized and stored in app state")

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

    # Unregister ORM events
    try:
        unregister_orm_events()
        logger.info("ORM events unregistered")
    except Exception as e:
        logger.warning("Error unregistering ORM events: {}", e)

    # Close Neo4j connection
    try:
        await app.state.neo4j_manager.close()
    except Exception as e:
        logger.error(f"Error closing Neo4j connection: {e}")

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
app.include_router(flags.router)
