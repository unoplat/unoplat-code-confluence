"""App interfaces activity for Temporal workflows."""

from __future__ import annotations

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_framework_repository import (
    db_get_all_framework_features_for_codebase,
    db_get_low_confidence_call_expression_candidates,
)
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    Interfaces,
)
from unoplat_code_confluence_query_engine.services.repository.app_interfaces_mapper import (
    build_interfaces_from_features,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    get_completion_namespaces,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_snapshot_writer,
)


class AppInterfacesActivity:
    """Activity for building app interfaces from PostgreSQL framework feature data."""

    @activity.defn
    async def build_app_interfaces(
        self,
        codebase_path: str,
        programming_language: str,
    ) -> Interfaces:
        """Build app interfaces from PostgreSQL framework feature data.

        Args:
            codebase_path: Path to the codebase for Postgres lookup
            programming_language: Programming language of the codebase

        Returns:
            Interfaces model with inbound, outbound, and internal constructs
        """
        logger.info(
            "[app_interfaces_activity] Building app interfaces for codebase: {}",
            codebase_path,
        )

        # Fetch all framework features from PostgreSQL
        features = await db_get_all_framework_features_for_codebase(
            codebase_path=codebase_path,
            programming_language=programming_language,
        )

        logger.info(
            "[app_interfaces_activity] Found {} framework features for codebase: {}",
            len(features),
            codebase_path,
        )

        # Build interfaces using mapper
        interfaces = build_interfaces_from_features(
            features=features,
            codebase_path=codebase_path,
        )

        logger.info(
            "[app_interfaces_activity] Built interfaces: {} inbound, {} outbound, {} internal constructs",
            len(interfaces.inbound_constructs),
            len(interfaces.outbound_constructs),
            len(interfaces.internal_constructs),
        )

        return interfaces

    @activity.defn
    async def fetch_low_confidence_call_expression_candidates(
        self,
        codebase_path: str,
        programming_language: str,
    ) -> list[dict[str, object]]:
        """Fetch low-confidence CallExpression candidates for validator processing.

        Args:
            codebase_path: Path to the codebase for PostgreSQL lookup.
            programming_language: Programming language of the codebase.

        Returns:
            Serialized candidate payloads for validator-agent execution.
        """
        candidates = await db_get_low_confidence_call_expression_candidates(
            codebase_path=codebase_path,
            programming_language=programming_language,
        )
        logger.info(
            "[app_interfaces_activity] Found {} low-confidence CallExpression candidates for codebase: {}",
            len(candidates),
            codebase_path,
        )
        return [candidate.model_dump(mode="json") for candidate in candidates]

    @activity.defn
    async def emit_app_interfaces_completion(
        self,
        repository_qualified_name: str,
        repository_workflow_run_id: str,
        codebase_name: str,
        programming_language: str,
    ) -> None:
        """Emit completion event for app_interfaces_agent progress tracking.

        Args:
            repository_qualified_name: Repository identifier (e.g., "owner/repo")
            repository_workflow_run_id: Unique workflow run ID for event tracking
            codebase_name: Name of the codebase being processed
            programming_language: Programming language of the codebase
        """
        if "/" not in repository_qualified_name:
            logger.warning(
                "[app_interfaces_activity] Invalid repository_qualified_name: {}",
                repository_qualified_name,
            )
            return

        owner_name, repo_name = repository_qualified_name.split("/", 1)
        writer = get_snapshot_writer()

        await writer.append_event_atomic(
            owner_name=owner_name,
            repo_name=repo_name,
            codebase_name=codebase_name,
            agent_name="app_interfaces_agent",
            phase="result",
            message="App interfaces completed",
            completion_namespaces=set(get_completion_namespaces(programming_language)),
            repository_workflow_run_id=repository_workflow_run_id,
        )

        logger.info(
            "[app_interfaces_activity] Emitted completion event for {}/{} codebase={}",
            owner_name,
            repo_name,
            codebase_name,
        )
