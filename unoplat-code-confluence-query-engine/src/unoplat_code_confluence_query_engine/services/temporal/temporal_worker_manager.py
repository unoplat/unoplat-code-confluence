"""Temporal worker manager for persistent worker lifecycle.

This module manages a persistent Temporal worker that is started at app
initialization and shared across all API requests. This avoids the overhead
of creating new workers per request.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import logfire
from loguru import logger
from pydantic_ai.durable_exec.temporal import (
    AgentPlugin,
    LogfirePlugin,
    PydanticAIPlugin,
)
import temporalio.api.workflowservice.v1 as wsv1
from temporalio.client import Client
from temporalio.common import VersioningBehavior, WorkerDeploymentVersion
from temporalio.worker import Interceptor, Worker, WorkerDeploymentConfig
from unoplat_code_confluence_commons.credential_enums import ProviderKey

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.config.model_factory import (
    ModelFactory,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.business_logic_post_process_activity import (
    BusinessLogicPostProcessActivity,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_db_activity import (
    CodebaseWorkflowDbActivity,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.dependency_guide_completion_activity import (
    DependencyGuideCompletionActivity,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.dependency_guide_fetch_activity import (
    DependencyGuideFetchActivity,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.repository_agent_snapshot_activity import (
    RepositoryAgentSnapshotActivity,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.repository_workflow_db_activity import (
    RepositoryWorkflowDbActivity,
)
from unoplat_code_confluence_query_engine.services.temporal.build_id_generator import (
    DEPLOYMENT_NAME,
    compute_credential_hash,
    generate_build_id,
)
from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_interceptor import (
    AgentWorkflowStatusInterceptor,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    ServiceRegistry,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
    get_temporal_agents,
    initialize_temporal_agents,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_workflows import (
    CodebaseAgentWorkflow,
    RepositoryAgentWorkflow,
)
from unoplat_code_confluence_query_engine.services.temporal.version_management import (
    set_current_version,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

# Task queue name for the agent workflows
TASK_QUEUE = "agent-queue"


def _setup_logfire(settings: EnvironmentSettings) -> logfire.Logfire:
    """Configure Logfire for the Temporal worker.

    Args:
        settings: Environment settings with Logfire configuration

    Returns:
        Configured Logfire instance
    """
    if settings.logfire_sdk_write_key:
        instance = logfire.configure(
            token=settings.logfire_sdk_write_key.get_secret_value(),
            service_name="unoplat-code-confluence-query-engine-worker",
            environment=settings.environment,
            send_to_logfire=True,
        )
        logger.debug("[temporal_worker_manager] Logfire configured with SDK write key")
    else:
        instance = logfire.configure(
            service_name="unoplat-code-confluence-query-engine-worker",
            environment=settings.environment,
            send_to_logfire="if-token-present",
        )
    logfire.instrument_pydantic_ai()
    return instance


class TemporalWorkerManager:
    """Manages the lifecycle of a persistent Temporal worker.

    This class handles:
    - Creating and connecting the Temporal client
    - Setting up the worker with all agent plugins
    - Running the worker in a background task
    - Graceful shutdown on app termination
    """

    def __init__(self) -> None:
        """Initialize the worker manager."""
        self._client: Client | None = None
        self._worker: Worker | None = None
        self._worker_task: asyncio.Task[None] | None = None
        self._registry: ServiceRegistry | None = None
        self._started: bool = False
        self._current_build_id: str | None = None

    @property
    def client(self) -> Client:
        """Get the connected Temporal client.

        Returns:
            Connected Temporal client instance

        Raises:
            RuntimeError: If worker manager not started
        """
        if not self._client:
            raise RuntimeError("TemporalWorkerManager not started. Call start() first.")
        return self._client

    @property
    def is_running(self) -> bool:
        """Check if the worker is running."""
        return self._started and self._worker_task is not None

    @property
    def current_build_id(self) -> str | None:
        """Get the current worker build ID.

        Returns:
            Current build ID if worker is running, None otherwise
        """
        return self._current_build_id

    async def start(
        self,
        *,
        settings: EnvironmentSettings,
        config: AiModelConfig | None = None,
        interceptors: Sequence[Interceptor] | None = None,
    ) -> None:
        """Start the Temporal client and worker.

        Args:
            settings: Environment settings with Temporal configuration
            config: Optional pre-loaded AI model config (avoids DB lookup)
            interceptors: Optional list of workflow interceptors to register
        """
        if self._started:
            logger.warning("[temporal_worker_manager] Worker already started, skipping")
            return

        temporal_address = settings.temporal_address
        namespace = settings.temporal_namespace

        logger.info(
            "[temporal_worker_manager] Starting Temporal worker: address={}, namespace={}, queue={}",
            temporal_address,
            namespace,
            TASK_QUEUE,
        )

        # Create Logfire setup function that captures settings
        def setup_logfire() -> logfire.Logfire:
            return _setup_logfire(settings)

        # Connect to Temporal server
        self._client = await Client.connect(
            temporal_address,
            namespace=namespace,
            plugins=[
                PydanticAIPlugin(),
                LogfirePlugin(setup_logfire=setup_logfire),
            ],
        )
        logger.info("[temporal_worker_manager] Connected to Temporal server")

        # Initialize service registry with MCP config
        self._registry = ServiceRegistry.get_instance()
        await self._registry.initialize(
            settings=settings,
            mcp_config_path=settings.mcp_servers_config_path,
        )
        logger.info(
            f"[temporal_worker_manager] Service registry initialized with MCP config: {settings.mcp_servers_config_path}"
        )

        # Inject Exa API key into MCP server config (static for worker lifecycle)
        async with get_startup_session() as session:
            exa_api_key = await CredentialsService.get_tool_credential(
                session, ProviderKey.EXA
            )
        if exa_api_key:
            updated = self._registry.mcp_server_manager.set_remote_server_query_param(
                "exa", "exaApiKey", exa_api_key
            )
            if updated:
                logger.info(
                    "[temporal_worker_manager] Exa MCP server API key injected into config"
                )
            else:
                logger.warning(
                    "[temporal_worker_manager] Exa MCP server config not found; key not applied"
                )
        else:
            logger.warning(
                "[temporal_worker_manager] Exa API key not configured; Exa MCP tools unavailable"
            )

        # Load model configuration (use passed config or load from database)
        if config is not None:
            model_config = config
            async with get_startup_session() as session:
                model, model_settings = await ModelFactory.build(
                    model_config, settings, session
                )
            logger.info(
                "[temporal_worker_manager] Using provided config: provider={}, model={}",
                model_config.provider_key,
                model_config.model_name,
            )
        else:
            async with get_startup_session() as session:
                model_config = await session.get(AiModelConfig, 1)
                if not model_config:
                    raise RuntimeError(
                        "No AI model configuration found in database. "
                        "Please configure the model via /ai-model-config endpoint first."
                    )
                model, model_settings = await ModelFactory.build(
                    model_config, settings, session
                )
            logger.info(
                "[temporal_worker_manager] Loaded model from database: provider={}, model={}",
                model_config.provider_key,
                model_config.model_name,
            )

        # Load credential and compute hash for build ID
        credential_hash: str | None = None
        async with get_startup_session() as session:
            credential = await CredentialsService.get_model_credential(session)
            if credential:
                credential_hash = compute_credential_hash(credential)

        # Generate build ID for worker versioning (includes credential hash)
        build_id = generate_build_id(model_config, credential_hash)
        logger.info(
            "[temporal_worker_manager] Generated build ID for worker versioning: {} (credential_included={})",
            build_id,
            credential_hash is not None,
        )

        # Initialize temporal agents with model from database
        # Note: initialize_temporal_agents creates its own TemporalAgentRetryConfig internally
        initialize_temporal_agents(model, settings, model_settings)
        logger.info(
            "[temporal_worker_manager] Temporal agents initialized with database model"
        )

        # Get temporal agents and create plugins
        temporal_agents = get_temporal_agents()
        agent_plugins: list[AgentPlugin] = [
            AgentPlugin(agent) for agent in temporal_agents.values()
        ]

        logger.info(
            "[temporal_worker_manager] Created {} agent plugins: {}",
            len(agent_plugins),
            list(temporal_agents.keys()),
        )

        # Create DB activity instances
        repo_db_activity = RepositoryWorkflowDbActivity()
        codebase_db_activity = CodebaseWorkflowDbActivity()
        snapshot_activity = RepositoryAgentSnapshotActivity()
        business_logic_post_process_activity = BusinessLogicPostProcessActivity()
        dependency_guide_completion_activity = DependencyGuideCompletionActivity()
        dependency_guide_fetch_activity = DependencyGuideFetchActivity()

        # Build interceptor list - always include status interceptor
        all_interceptors: list[Interceptor] = [AgentWorkflowStatusInterceptor()]
        if interceptors:
            all_interceptors.extend(interceptors)
        logger.info(
            "[temporal_worker_manager] Registered {} interceptors: {}",
            len(all_interceptors),
            [type(i).__name__ for i in all_interceptors],
        )

        # Create worker deployment config for versioning
        deployment_config = WorkerDeploymentConfig(
            version=WorkerDeploymentVersion(
                deployment_name=DEPLOYMENT_NAME,
                build_id=build_id,
            ),
            use_worker_versioning=True,
            default_versioning_behavior=VersioningBehavior.AUTO_UPGRADE,
        )
        logger.info(
            "[temporal_worker_manager] Worker deployment config: deployment={}, build_id={}",
            DEPLOYMENT_NAME,
            build_id,
        )

        # Create worker with workflows, activities, agent plugins, and interceptors
        self._worker = Worker(
            self._client,
            task_queue=TASK_QUEUE,
            workflows=[
                RepositoryAgentWorkflow,
                CodebaseAgentWorkflow,
            ],
            activities=[
                repo_db_activity.update_repository_workflow_status,
                codebase_db_activity.update_codebase_workflow_status,
                snapshot_activity.persist_agent_snapshot_complete,
                business_logic_post_process_activity.post_process_business_logic,
                dependency_guide_completion_activity.emit_dependency_guide_completion,
                dependency_guide_fetch_activity.fetch_codebase_dependencies,
            ],
            plugins=agent_plugins,
            interceptors=all_interceptors,
            deployment_config=deployment_config,
        )

        # Store build ID for tracking
        self._current_build_id = build_id

        # Run worker in background task FIRST (must poll before deployment can be registered)
        self._worker_task = asyncio.create_task(
            self._run_worker(),
            name="temporal-worker",
        )

        # Wait for worker to register, then set as current version (in background)
        # This follows the official Temporal pattern from:
        # https://github.com/temporalio/samples-python/blob/main/worker_versioning/app.py
        asyncio.create_task(
            self._wait_and_set_current_version(build_id),
            name="set-current-version",
        )

        self._started = True

        logger.info("[temporal_worker_manager] Temporal worker started successfully")

    async def _run_worker(self) -> None:
        """Run the worker until cancelled."""
        if not self._worker:
            return

        try:
            logger.info("[temporal_worker_manager] Worker polling started")
            await self._worker.run()
        except asyncio.CancelledError:
            logger.info("[temporal_worker_manager] Worker cancelled, shutting down")
            raise
        except Exception as e:
            logger.exception("[temporal_worker_manager] Worker error: {}", e)
            raise

    async def _wait_and_set_current_version(self, build_id: str) -> None:
        """Wait for worker deployment to register, then set as current version.

        This follows the official Temporal pattern from:
        https://github.com/temporalio/samples-python/blob/main/worker_versioning/app.py

        A Worker Deployment only exists after a worker with that deployment
        configuration has successfully polled the Temporal server.

        Args:
            build_id: The build ID to wait for and set as current
        """
        if not self._client:
            logger.error("[temporal_worker_manager] Client not initialized")
            return

        target_version = WorkerDeploymentVersion(
            deployment_name=DEPLOYMENT_NAME,
            build_id=build_id,
        )

        logger.info(
            "[temporal_worker_manager] Waiting for worker deployment to register: deployment={}, build_id={}",
            DEPLOYMENT_NAME,
            build_id,
        )

        # Poll until worker version appears on the server
        while True:
            try:
                describe_request = wsv1.DescribeWorkerDeploymentRequest(
                    namespace=self._client.namespace,
                    deployment_name=DEPLOYMENT_NAME,
                )
                response = (
                    await self._client.workflow_service.describe_worker_deployment(
                        describe_request
                    )
                )

                # Check if our target version is registered
                for (
                    version_summary
                ) in response.worker_deployment_info.version_summaries:
                    if (
                        version_summary.deployment_version.deployment_name
                        == target_version.deployment_name
                        and version_summary.deployment_version.build_id
                        == target_version.build_id
                    ):
                        # Version found! Break out of for loop
                        break
                else:
                    # Version not found yet (for loop completed without break)
                    await asyncio.sleep(1)
                    continue

                # Break out of while loop - version was found
                break

            except Exception as e:
                # Deployment might not exist yet, wait and retry
                logger.debug(
                    "[temporal_worker_manager] Waiting for deployment registration (retrying): {}",
                    str(e),
                )
                await asyncio.sleep(1)

        # Now safe to set as current (version confirmed to exist)
        await set_current_version(self._client, build_id)
        logger.info(
            f"[temporal_worker_manager] Worker deployment registered and set as current: build_id={build_id}"
        )

    async def stop(self) -> None:
        """Stop the worker and cleanup resources."""
        if not self._started:
            logger.debug(
                "[temporal_worker_manager] Worker not started, nothing to stop"
            )
            return

        logger.info("[temporal_worker_manager] Stopping Temporal worker...")

        # Cancel worker task
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        # Shutdown service registry
        if self._registry:
            await self._registry.shutdown()

        self._worker = None
        self._worker_task = None
        self._client = None
        self._registry = None
        self._started = False
        self._current_build_id = None

        logger.info("[temporal_worker_manager] Temporal worker stopped")


# Global singleton instance
_worker_manager: TemporalWorkerManager | None = None


def get_worker_manager() -> TemporalWorkerManager:
    """Get the global TemporalWorkerManager instance.

    Creates a new instance if one doesn't exist.

    Returns:
        The global TemporalWorkerManager instance
    """
    global _worker_manager
    if _worker_manager is None:
        _worker_manager = TemporalWorkerManager()
    return _worker_manager
