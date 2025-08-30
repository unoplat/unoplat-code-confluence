from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase
from unoplat_code_confluence_commons.flags import Flag

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    create_code_confluence_agents,
)
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
    get_session,
    init_db_connections,
)
from unoplat_code_confluence_query_engine.services.ai_model_config_service import (
    AiModelConfigService,
)
from unoplat_code_confluence_query_engine.services.config_hot_reload import (
    register_orm_events,
    unregister_orm_events,
)
from unoplat_code_confluence_query_engine.services.flag_service import FlagService
from unoplat_code_confluence_query_engine.services.mcp.mcp_server_manager import (
    MCPServerManager,
)
from unoplat_code_confluence_query_engine.services.model_factory import ModelFactory


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

    # Initialize MCP servers
    app.state.mcp_manager = MCPServerManager()
    await app.state.mcp_manager.load_config(app.state.settings.mcp_servers_config_path)
    await app.state.mcp_manager.start_servers()
    # Store MCP server instances in app state for agent integration
    app.state.mcp_servers = app.state.mcp_manager.get_servers()

    # Initialize services and store in app state
    app.state.ai_model_config_service = AiModelConfigService()
    app.state.flag_service = FlagService()
    logger.info("Services initialized and stored in app state")

    # Load AI model configuration
    async with get_session() as session:
        result = await session.execute(select(AiModelConfig).where(AiModelConfig.id == 1))
        config = result.scalar_one_or_none()

    # Initialize agents using model config outside of DB transaction
    if config:
        try:
            model_factory = ModelFactory()
            model, model_settings = await model_factory.build(config)
            app.state.model = model
            logger.debug(
                "Initializing agents with model: {}/{} and settings present? {}",
                config.provider_key,
                config.model_name,
                bool(model_settings),
            )
            app.state.agents = create_code_confluence_agents(app.state.mcp_manager, model, model_settings)
            logger.info("Agents initialized with model: {}/{}", config.provider_key, config.model_name)
            logger.debug(
                "Agent registry initialized: {} agents -> {}",
                len(app.state.agents),
                list(app.state.agents.keys()),
            )

            # Sanity check for required agents
            required_agents = [
                "directory_agent",
                "framework_explorer_agent",
                "development_workflow_agent",
                "business_logic_domain_agent",
            ]
            missing = [a for a in required_agents if a not in app.state.agents]
            if missing:
                logger.error("Missing required agents at startup: {}", missing)
            else:
                logger.debug("All required agents present at startup")
        except Exception as e:
            logger.error("Failed to initialize model from config: {}", e)
            app.state.model = None
            app.state.agents = {}
    else:
        # No configuration - agents remain uninitialized
        app.state.model = None
        app.state.agents = {}
        logger.warning("No AI model configuration found. Agents not initialized.")
        logger.debug("Agent registry is empty at startup")

    # Ensure isModelConfigured flag reflects current state in a fresh transaction
    async with get_session() as session:
        flag_result = await session.execute(select(Flag).where(Flag.name == "isModelConfigured"))
        flag = flag_result.scalar_one_or_none()
        if flag:
            flag.status = config is not None
        else:
            session.add(Flag(name="isModelConfigured", status=config is not None))

    yield

    # Shutdown
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
        logger.error("Error closing Neo4j connection: {}", e)

    # Stop MCP servers
    try:
        await app.state.mcp_manager.stop_servers()
    except Exception as e:
        logger.error("Error stopping MCP servers: {}", e)

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
