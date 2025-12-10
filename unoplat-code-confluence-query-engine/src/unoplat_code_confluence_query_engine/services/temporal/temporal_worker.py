"""Temporal worker setup for durable agent execution.

This module configures and runs the Temporal worker with all
agent plugins registered.
"""

from pathlib import Path

from loguru import logger
from pydantic_ai.durable_exec.temporal import AgentPlugin, PydanticAIPlugin
from temporalio.client import Client
from temporalio.worker import Worker

from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
    get_temporal_agents,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_workflows import (
    CodebaseAgentWorkflow,
    RepositoryAgentWorkflow,
)

# Task queue name for the agent workflows
TASK_QUEUE = "agent-queue"

# Default MCP config path (relative to project root)
MCP_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "mcp-servers.json"


async def create_worker(
    temporal_address: str = "localhost:7233",
    namespace: str = "default",
    task_queue: str = TASK_QUEUE,
    additional_plugins: list[AgentPlugin] | None = None,
) -> Worker:
    """Create a Temporal worker with all agent plugins.

    Args:
        temporal_address: Temporal server address
        namespace: Temporal namespace
        task_queue: Task queue name
        additional_plugins: Optional list of additional AgentPlugins to register

    Returns:
        Configured Worker instance
    """
    logger.debug("[temporal_worker] create_worker START")
    logger.info(
        f"[temporal_worker] Connecting to Temporal server at {temporal_address} for task queue {task_queue}"
    )

    # Connect to Temporal with PydanticAI plugin for serialization
    logger.debug("[temporal_worker] Creating Temporal client...")
    client = await Client.connect(
        temporal_address,
        namespace=namespace,
        plugins=[PydanticAIPlugin()],
    )
    logger.debug("[temporal_worker] Temporal client connected")

    # Get temporal agents
    logger.debug("[temporal_worker] Getting temporal agents...")
    temporal_agents = get_temporal_agents()
    logger.debug("[temporal_worker] Got {} temporal agents", len(temporal_agents))

    # Create agent plugins for each temporal agent
    logger.debug("[temporal_worker] Creating AgentPlugins...")
    agent_plugins: list[AgentPlugin] = [
        AgentPlugin(agent) for agent in temporal_agents.values()
    ]
    logger.debug("[temporal_worker] Created {} AgentPlugins", len(agent_plugins))

    # Add any additional plugins (e.g., Context7 TemporalAgent)
    if additional_plugins:
        logger.debug(
            "[temporal_worker] Adding {} additional plugins", len(additional_plugins)
        )
        agent_plugins.extend(additional_plugins)

    logger.info(
        f"[temporal_worker] Creating worker with {len(agent_plugins)} agent plugins: {list(temporal_agents.keys()) + (['context7_agent'] if additional_plugins else [])}"
    )

    # Create worker with workflows and agent plugins
    logger.debug("[temporal_worker] Instantiating Worker...")
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[
            RepositoryAgentWorkflow,
            CodebaseAgentWorkflow,
        ],
        plugins=agent_plugins,
    )
    logger.debug("[temporal_worker] Worker instantiated")

    return worker
