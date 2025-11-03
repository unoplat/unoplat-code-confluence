"""Unified agent execution service consolidating duplicated logic."""

import asyncio
from dataclasses import asdict
from datetime import datetime
from functools import partial
from pathlib import Path
import time
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, List, Optional, Union
import uuid

from fastapi import Request
from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
)

from unoplat_code_confluence_query_engine.db.repository_agent_snapshot_service import (
    RepositoryAgentSnapshotWriter,
)
from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.models.agent_execution_request import (
    AgentExecutionRequest,
)

# NOTE: Keep model imports minimal to avoid unused warnings; AgentMdOutput not needed here.
from unoplat_code_confluence_query_engine.models.agent_md_aggregate import (
    AgentMdAggregate,
)
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    BusinessLogicDomain,
    DevelopmentWorkflow,
    ProgrammingLanguageMetadataOutput,
    ProjectConfiguration,
)
from unoplat_code_confluence_query_engine.models.agent_usage_statistics import (
    UsageStatistics,
    UsageSummary,
    WorkflowStatistics,
)
from unoplat_code_confluence_query_engine.models.repository_ruleset_metadata import (
    CodebaseMetadata,
    RepositoryRulesetMetadata,
)
from unoplat_code_confluence_query_engine.services.agent_prompt_registry import (
    AgentPromptRegistry,
)
from unoplat_code_confluence_query_engine.services.library_documentation_service import (
    LibraryDocumentationService,
)
from unoplat_code_confluence_query_engine.services.mock_sse_service import (
    MockSSEService,
)
from unoplat_code_confluence_query_engine.services.package_manager_metadata_service import (
    fetch_programming_language_metadata,
)
from unoplat_code_confluence_query_engine.services.post_processing_service import (
    PostProcessingService,
)
from unoplat_code_confluence_query_engine.services.repository_event_progress_tracker import (
    RepositoryEventProgressTracker,
)
from unoplat_code_confluence_query_engine.services.tool_message_policy import (
    DefaultToolMessagePolicy,
)
from unoplat_code_confluence_query_engine.utils.agent_error_logger import (
    log_agent_error,
)
from unoplat_code_confluence_query_engine.utils.agent_logs import (
    get_logs_subdir,
    resolve_logs_dir,
)

# Removed _normalize_object_for_json and _convert_to_json_string functions
# as per refactor plan to eliminate JSON conversions in pipeline


class AgentExecutionService:
    """Unified service for executing agents with consistent streaming and node management."""

    def __init__(self, logs_dir: Union[str, Path, None] = None) -> None:
        """Initialize the unified agent execution service.

        Args:
            logs_dir: Directory path for storing execution logs and nodes
        """
        self.logs_dir = (
            resolve_logs_dir(logs_dir)
            if logs_dir is not None
            else get_logs_subdir("agent_runs")
        )
        self.prompt_provider = AgentPromptRegistry()
        self.tool_message_policy = DefaultToolMessagePolicy()
        self.post_processing = PostProcessingService()

    async def start_repository_workflow(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        request: Request,
        repository_workflow_run_id: Optional[str] = None,
    ) -> str:
        """Kick off repository workflow execution and return the workflow run identifier."""

        owner_name, repo_name = self._parse_repository_name(
            ruleset_metadata.repository_qualified_name
        )
        snapshot_writer = RepositoryAgentSnapshotWriter(owner_name, repo_name)

        try:
            settings = request.app.state.settings  # type: ignore[attr-defined]
        except AttributeError:
            settings = None

        mock_run_id: Optional[str] = None
        if settings and getattr(settings, "mock_sse_enabled", False):
            mock_service_instance = MockSSEService(
                events_file_path=settings.mock_sse_log_path,
                result_file_path=settings.mock_sse_result_path,
            )
            mock_run_id = mock_service_instance.repository_workflow_run_id

        existing_run_id = await snapshot_writer.get_active_run_id()
        if existing_run_id is not None:
            if (
                repository_workflow_run_id
                and repository_workflow_run_id != existing_run_id
            ):
                logger.info(
                    "Workflow {} already running for {}/{}; ignoring requested id {}",
                    existing_run_id,
                    owner_name,
                    repo_name,
                    repository_workflow_run_id,
                )
            else:
                logger.info(
                    "Workflow {} already running for {}/{}; returning existing identifier",
                    existing_run_id,
                    owner_name,
                    repo_name,
                )
            return existing_run_id

        workflow_run_id = repository_workflow_run_id or mock_run_id or uuid.uuid4().hex
        asyncio.create_task(
            self._run_repository_workflow(
                ruleset_metadata=ruleset_metadata,
                request=request,
                repository_workflow_run_id=workflow_run_id,
            )
        )
        return workflow_run_id

    async def _run_repository_workflow(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        request: Request,
        repository_workflow_run_id: str,
    ) -> None:
        """Background task that executes all codebase agents and persists progress."""

        owner_name, repo_name = self._parse_repository_name(
            ruleset_metadata.repository_qualified_name
        )
        snapshot_writer = RepositoryAgentSnapshotWriter(owner_name, repo_name)
        codebase_names = [
            codebase.codebase_name for codebase in ruleset_metadata.codebase_metadata
        ]

        completion_namespaces = {
            "project_configuration_agent",
            "development_workflow",
            "business_logic_domain",
        }

        connection_id = repository_workflow_run_id[:8]
        progress_tracker = RepositoryEventProgressTracker(
            snapshot_writer,
            repository_qualified_name=ruleset_metadata.repository_qualified_name,
            connection_id=connection_id,
            owner_name=owner_name,
            repo_name=repo_name,
            codebase_names=codebase_names,
            completion_namespaces=completion_namespaces,
        )

        try:
            await snapshot_writer.begin_run(
                repository_qualified_name=ruleset_metadata.repository_qualified_name,
                repository_workflow_run_id=repository_workflow_run_id,
                codebase_names=codebase_names,
            )
        except Exception as status_error:  # noqa: BLE001
            logger.warning(
                "Workflow {} failed to initialize snapshot for {}/{}: {}",
                repository_workflow_run_id,
                owner_name,
                repo_name,
                status_error,
            )

        try:
            settings = request.app.state.settings  # type: ignore[attr-defined]
        except AttributeError as exc:  # noqa: BLE001
            raise RuntimeError(
                "Application settings not initialized on app.state"
            ) from exc

        if settings.mock_sse_enabled:
            await self._run_mock_repository_workflow(
                ruleset_metadata=ruleset_metadata,
                request=request,
                repository_workflow_run_id=repository_workflow_run_id,
                snapshot_writer=snapshot_writer,
                progress_tracker=progress_tracker,
                events_path=settings.mock_sse_log_path,
                result_path=settings.mock_sse_result_path,
                delay_seconds=settings.mock_sse_delay_seconds,
            )
            return

        aggregators = await self._initialize_aggregators(
            ruleset_metadata=ruleset_metadata,
            request=request,
        )

        try:
            agents = request.app.state.agents  # type: ignore[attr-defined]
        except AttributeError as agent_error:  # noqa: BLE001
            raise RuntimeError(
                "Agents not initialized on application state"
            ) from agent_error

        required_agents = [
            "project_configuration_agent",
            "development_workflow_agent",
            "business_logic_domain_agent",
        ]
        missing_agents = [name for name in required_agents if name not in agents]
        if missing_agents:
            raise RuntimeError(
                "Agents not initialized or missing: " + ", ".join(missing_agents)
            )

        project_structure_by_codebase: Dict[str, ProjectConfiguration] = {}
        event_id = 0
        workflow_usage: Dict[str, Dict[str, UsageSummary]] = {}

        try:
            project_configuration_request = AgentExecutionRequest(
                agent_name="project_configuration_agent",
                agent=agents["project_configuration_agent"],
                fastapi_request=request,
                event_namespace="project_configuration_agent",
            )

            directory_result_handler = partial(
                self._update_directory_result,
                aggregators,
                project_structure_by_codebase,
            )

            event_id, project_config_usage = await self._collect_agent_stream(
                ruleset_metadata=ruleset_metadata,
                exec_request=project_configuration_request,
                progress_tracker=progress_tracker,
                starting_event_id=event_id,
                on_result=directory_result_handler,
            )
            workflow_usage["project_configuration_agent"] = project_config_usage

            development_request = AgentExecutionRequest(
                agent_name="development_workflow",
                agent=agents["development_workflow_agent"],
                fastapi_request=request,
                event_namespace="development_workflow",
                extra_prompt_context={
                    "project_structure": project_structure_by_codebase
                },
            )

            workflow_result_handler = partial(
                self._update_workflow_result,
                aggregators,
            )

            event_id, development_workflow_usage = await self._collect_agent_stream(
                ruleset_metadata=ruleset_metadata,
                exec_request=development_request,
                progress_tracker=progress_tracker,
                starting_event_id=event_id,
                on_result=workflow_result_handler,
            )
            workflow_usage["development_workflow"] = development_workflow_usage

            business_logic_request = AgentExecutionRequest(
                agent_name="business_logic_domain",
                agent=agents["business_logic_domain_agent"],
                fastapi_request=request,
                event_namespace="business_logic_domain",
                postprocess_enabled=True,
            )

            business_logic_handler = partial(
                self._update_business_logic_result,
                aggregators,
            )

            event_id, business_logic_usage = await self._collect_agent_stream(
                ruleset_metadata=ruleset_metadata,
                exec_request=business_logic_request,
                progress_tracker=progress_tracker,
                starting_event_id=event_id,
                on_result=business_logic_handler,
            )
            workflow_usage["business_logic_domain"] = business_logic_usage

            await progress_tracker.append_final_events(event_id)

            final_payload, statistics_payload = self._build_final_payload(
                ruleset_metadata=ruleset_metadata,
                aggregators=aggregators,
                workflow_usage=workflow_usage,
            )

            await snapshot_writer.complete_run(
                final_payload=final_payload,
                statistics_payload=statistics_payload,
            )
        except Exception as execution_error:  # noqa: BLE001
            logger.exception(
                "Workflow {} for {}/{} failed: {}",
                repository_workflow_run_id,
                owner_name,
                repo_name,
                execution_error,
            )
            try:
                await snapshot_writer.fail_run(
                    error_payload={"error": str(execution_error)}
                )
            except Exception as status_error:  # noqa: BLE001
                logger.warning(
                    "Workflow {} failed to mark snapshot as errored for {}/{}: {}",
                    repository_workflow_run_id,
                    owner_name,
                    repo_name,
                    status_error,
                )

    async def _run_mock_repository_workflow(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        request: Request,
        repository_workflow_run_id: str,
        snapshot_writer: RepositoryAgentSnapshotWriter,
        progress_tracker: RepositoryEventProgressTracker,
        events_path: str,
        result_path: str,
        delay_seconds: float,
    ) -> None:
        """Replay mock events and persist them using the standard tracker."""

        mock_service = MockSSEService(events_path, result_path)

        if not mock_service.has_events():
            logger.error(
                "Workflow {} mock events unavailable, aborting",
                repository_workflow_run_id,
            )
            await snapshot_writer.fail_run(
                error_payload={"error": "mock events unavailable"}
            )
            return

        event_counter = 0
        counter_lock = asyncio.Lock()

        delay = max(delay_seconds, 0.0)

        async def play_codebase_events(codebase_entry: Dict[str, Any]) -> None:
            nonlocal event_counter
            codebase_name = codebase_entry.get("codebase_name", "unknown")
            events = codebase_entry.get("events", [])

            for event in events:
                await asyncio.sleep(delay)

                raw_event_name = event.get("event") or ""
                parts = raw_event_name.split(":", 2) if raw_event_name else []
                namespace: str | None = None
                resolved_phase = event.get("phase")

                if len(parts) == 3:
                    _, namespace, trailing_phase = parts
                    if not resolved_phase:
                        resolved_phase = trailing_phase
                elif len(parts) == 2:
                    _, namespace = parts

                if namespace is None:
                    namespace = event.get("namespace")

                if namespace is None:
                    logger.debug(
                        "Mock event missing namespace for codebase {}: {}",
                        codebase_name,
                        raw_event_name,
                    )
                    namespace = "unknown"

                if not resolved_phase:
                    resolved_phase = "unknown"

                resolved_event_name = f"{codebase_name}:{namespace}:{resolved_phase}"

                message = event.get("message")
                if message is not None and not isinstance(message, str):
                    message = str(message)

                event_payload = {k: v for k, v in event.items() if k != "event"}
                event_payload["message"] = message
                event_payload["phase"] = resolved_phase
                event_payload.setdefault("id", event.get("id"))

                async with counter_lock:
                    current_event_id = event_counter
                    event_counter += 1

                await progress_tracker.persist_codebase_event(
                    resolved_event_name,
                    event_payload,
                    current_event_id,
                )

        playback_tasks = [
            play_codebase_events(codebase_entry)
            for codebase_entry in mock_service.iter_codebase_events()
            if codebase_entry.get("events")
        ]

        if playback_tasks:
            await asyncio.gather(*playback_tasks)

        await progress_tracker.append_final_events(event_counter)

        final_payload = mock_service.get_final_payload()
        final_payload["repository_workflow_run_id"] = repository_workflow_run_id
        if "repository" not in final_payload and mock_service.repository_name:
            final_payload["repository"] = mock_service.repository_name

        await snapshot_writer.complete_run(final_payload=final_payload)

    async def _collect_agent_stream(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        exec_request: AgentExecutionRequest,
        progress_tracker: RepositoryEventProgressTracker,
        starting_event_id: int,
        on_result: Optional[Callable[[str, Any], Awaitable[None]]] = None,
    ) -> tuple[int, Dict[str, UsageSummary]]:
        """Collect streaming events for a single agent and persist them."""

        event_id = starting_event_id
        agent_usage_data: Dict[str, UsageSummary] = {}

        async for progress_event in self.run_stream(
            ruleset_metadata,
            request=exec_request,
        ):
            event_name = progress_event.get("event", "")
            event_data = progress_event.get("data", {})

            if on_result and event_name:
                target_namespace = (
                    exec_request.event_namespace or exec_request.agent_name
                )
                if event_name.endswith(f":{target_namespace}:result"):
                    parts = event_name.split(":", 2)
                    if len(parts) == 3:
                        codebase_name = parts[0]
                        result_payload = event_data.get("result")
                        if result_payload is not None:
                            await on_result(codebase_name, result_payload)

            # Capture usage statistics from completion events
            if event_name and event_name.endswith(":complete"):
                parts = event_name.split(":", 2)
                if len(parts) == 3:
                    codebase_name = parts[0]
                    usage = event_data.get("usage")
                    cost_usd = event_data.get("cost_usd")

                    if usage is not None:
                        agent_usage_data[codebase_name] = UsageSummary(
                            usage=usage,
                            cost_usd=cost_usd,
                        )
                        # Log what was collected
                        total_tokens = (
                            usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                            if isinstance(usage, dict)
                            else "unknown"
                        )
                        cost_str = f"{cost_usd:.6f}" if cost_usd is not None else "N/A"
                        logger.info(
                            "Collected usage for codebase {}: tokens={}, cost=${} USD",
                            codebase_name,
                            total_tokens,
                            cost_str,
                        )

            await progress_tracker.persist_codebase_event(
                event_name,
                event_data,
                event_id,
            )
            event_id += 1

        return (event_id, agent_usage_data)

    async def _initialize_aggregators(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        request: Request,
    ) -> Dict[str, AgentMdAggregate]:
        """Build per-codebase aggregators with language metadata seeded."""

        aggregators: Dict[str, AgentMdAggregate] = {}
        underscore_qualified = ruleset_metadata.repository_qualified_name.replace(
            "/",
            "_",
        )

        for codebase in ruleset_metadata.codebase_metadata:
            aggregator = AgentMdAggregate(codebase)
            language_metadata: Optional[ProgrammingLanguageMetadataOutput] = None
            try:
                language_metadata = await fetch_programming_language_metadata(
                    request.app.state.neo4j_manager,  # type: ignore[attr-defined]
                    underscore_qualified,
                    codebase.codebase_path,
                )
            except Exception as metadata_error:  # noqa: BLE001
                logger.debug(
                    "Failed to load language metadata for {}/{}: {}",
                    ruleset_metadata.repository_qualified_name,
                    codebase.codebase_name,
                    metadata_error,
                )

            aggregator.set_language_metadata(language_metadata)
            aggregators[codebase.codebase_name] = aggregator

        return aggregators

    async def _update_directory_result(
        self,
        aggregators: Dict[str, AgentMdAggregate],
        project_structure_by_codebase: Dict[str, ProjectConfiguration],
        codebase_name: str,
        result: ProjectConfiguration,
    ) -> None:
        """Update directory agent aggregation and cached structure."""

        project_structure_by_codebase[codebase_name] = result
        aggregators[codebase_name].update_from_project_configuration_agent(result)

    async def _update_workflow_result(
        self,
        aggregators: Dict[str, AgentMdAggregate],
        codebase_name: str,
        result: DevelopmentWorkflow,
    ) -> None:
        """Update development workflow aggregation."""

        aggregators[codebase_name].update_from_development_workflow(result)

    async def _update_business_logic_result(
        self,
        aggregators: Dict[str, AgentMdAggregate],
        codebase_name: str,
        result: BusinessLogicDomain,
    ) -> None:
        """Update business logic aggregation."""

        aggregators[codebase_name].update_from_business_logic(result)

    def _build_workflow_statistics(
        self,
        *,
        workflow_usage: Dict[str, Dict[str, UsageSummary]],
    ) -> Dict[str, Any]:
        """Build workflow statistics by aggregating usage across agents per codebase.

        Args:
            workflow_usage: Nested dict: {agent_name: {codebase_name: UsageSummary}}

        Returns:
            Statistics payload with per-codebase and total aggregations
        """
        # Log statistics building start
        logger.info("Building workflow statistics from {} agents", len(workflow_usage))
        for agent_name, codebase_usages in workflow_usage.items():
            logger.debug("Agent {}: {} codebases with usage data", agent_name, len(codebase_usages))

        # Aggregate per codebase across all agents
        codebase_stats: Dict[str, UsageStatistics] = {}

        # Collect all codebase names
        all_codebases: set[str] = set()
        for agent_usage in workflow_usage.values():
            all_codebases.update(agent_usage.keys())

        # Aggregate usage for each codebase
        for codebase_name in all_codebases:
            total_requests = 0
            total_input_tokens = 0
            total_output_tokens = 0
            total_cache_write_tokens = 0
            total_cache_read_tokens = 0
            total_tool_calls = 0
            total_cost = 0.0

            for agent_usage in workflow_usage.values():
                if codebase_name in agent_usage:
                    summary = agent_usage[codebase_name]
                    usage = summary.usage

                    total_requests += usage.get("requests", 0)
                    total_input_tokens += usage.get("input_tokens", 0)
                    total_output_tokens += usage.get("output_tokens", 0)
                    total_cache_write_tokens += usage.get("cache_write_tokens", 0)
                    total_cache_read_tokens += usage.get("cache_read_tokens", 0)
                    total_tool_calls += usage.get("tool_calls", 0)

                    if summary.cost_usd is not None:
                        total_cost += summary.cost_usd

            codebase_stats[codebase_name] = UsageStatistics(
                requests=total_requests,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                cache_write_tokens=total_cache_write_tokens,
                cache_read_tokens=total_cache_read_tokens,
                total_tokens=total_input_tokens + total_output_tokens,
                tool_calls=total_tool_calls,
                estimated_cost_usd=total_cost if total_cost > 0 else None,
            )

        # Calculate workflow totals from codebase stats
        workflow_stats = WorkflowStatistics(
            total_requests=sum(s.requests for s in codebase_stats.values()),
            total_input_tokens=sum(s.input_tokens for s in codebase_stats.values()),
            total_output_tokens=sum(s.output_tokens for s in codebase_stats.values()),
            total_cache_write_tokens=sum(
                s.cache_write_tokens for s in codebase_stats.values()
            ),
            total_cache_read_tokens=sum(
                s.cache_read_tokens for s in codebase_stats.values()
            ),
            total_tokens=sum(s.total_tokens for s in codebase_stats.values()),
            total_tool_calls=sum(s.tool_calls for s in codebase_stats.values()),
            total_estimated_cost_usd=sum(
                s.estimated_cost_usd
                for s in codebase_stats.values()
                if s.estimated_cost_usd is not None
            )
            or None,
            by_codebase=codebase_stats,
        )

        # Log statistics summary
        cost_str = (
            f"{workflow_stats.total_estimated_cost_usd:.6f}"
            if workflow_stats.total_estimated_cost_usd is not None
            else "N/A"
        )
        logger.info(
            "Workflow statistics generated: total_tokens={}, total_requests={}, total_cost=${} USD",
            workflow_stats.total_tokens,
            workflow_stats.total_requests,
            cost_str,
        )

        return workflow_stats.model_dump(exclude_none=True)

    def _build_final_payload(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        aggregators: Dict[str, AgentMdAggregate],
        workflow_usage: Dict[str, Dict[str, UsageSummary]],
    ) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """Build the final payload persisted in the snapshot row."""

        payload: Dict[str, Any] = {
            "repository": ruleset_metadata.repository_qualified_name,
            "codebases": {},
        }

        for codebase_name, aggregator in aggregators.items():
            final_model = aggregator.to_final_model()
            payload["codebases"][codebase_name] = final_model.model_dump_json(
                exclude_none=True
            )

        # Build statistics payload
        statistics_payload: Optional[Dict[str, Any]] = None
        try:
            statistics_payload = self._build_workflow_statistics(
                workflow_usage=workflow_usage
            )
        except Exception as stats_error:  # noqa: BLE001
            logger.warning(
                "Failed to build workflow statistics for {}: {}",
                ruleset_metadata.repository_qualified_name,
                stats_error,
            )

        return (payload, statistics_payload)

    @staticmethod
    def _parse_repository_name(repository_qualified_name: str) -> tuple[str, str]:
        """Split the repository qualified name into owner/repo components."""

        owner, _, repo = repository_qualified_name.partition("/")
        if not owner or not repo:
            raise ValueError(
                f"Invalid repository qualified name: {repository_qualified_name}"
            )
        return owner, repo

    async def run_stream(
        self,
        ruleset_metadata: RepositoryRulesetMetadata,
        *,
        request: AgentExecutionRequest,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run one agent per codebase concurrently and stream unified events.

        Args:
            ruleset_metadata: Repository and codebase metadata
            request: Agent execution configuration with FastAPI request for app.state access

        Yields:
            Standardized SSE events with format {codebase}:{agent}:{phase}
        """
        event_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=300)

        # Start concurrent tasks for each codebase
        tasks = []
        for codebase in ruleset_metadata.codebase_metadata:
            task = asyncio.create_task(
                self._stream_events_for_codebase(
                    ruleset_metadata.repository_qualified_name,
                    codebase,
                    request,
                    event_queue,
                )
            )
            tasks.append(task)

        # Stream events until all producers signal completion
        queue_wait_start = None
        total_queue_waits = 0
        max_queue_wait = 0.0
        producers_remaining = len(tasks)

        try:
            while producers_remaining > 0:
                try:
                    queue_wait_start = time.time()
                    event = await asyncio.wait_for(event_queue.get(), timeout=1.0)

                    # Log successful event retrieval
                    wait_time = time.time() - queue_wait_start
                    total_queue_waits += 1
                    max_queue_wait = max(max_queue_wait, wait_time)

                    # Check for producer done signal
                    if event.get("__done__") is True:
                        producers_remaining -= 1
                        logger.debug(
                            "Producer completed, {} remaining", producers_remaining
                        )
                        continue  # Don't yield the done signal itself

                    yield event

                except asyncio.TimeoutError:
                    # Log timeout but continue
                    if queue_wait_start:
                        wait_time = time.time() - queue_wait_start
                        logger.trace(
                            "Queue timeout after {:.2f}s (normal during processing)",
                            wait_time,
                        )
                    continue

            logger.debug(
                "All producers complete: total_waits={}, max_wait={:.2f}s",
                total_queue_waits,
                max_queue_wait,
            )
        except Exception as e:
            logger.error("Error in stream processing: {}", e)
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        finally:
            pass  # No cleanup needed for producer-based completion

    async def run(
        self,
        ruleset_metadata: RepositoryRulesetMetadata,
        *,
        request: AgentExecutionRequest,
    ) -> str:
        """Run one agent per codebase concurrently and return combined output.

        Args:
            ruleset_metadata: Repository and codebase metadata
            request: Agent execution configuration with FastAPI request for app.state access

        Returns:
            Combined markdown output from all codebases
        """
        tasks = []
        for codebase in ruleset_metadata.codebase_metadata:
            task = asyncio.create_task(
                self._run_agent_for_codebase(
                    ruleset_metadata.repository_qualified_name,
                    codebase,
                    request,
                )
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return self._combine_codebase_outputs(results, ruleset_metadata)

    def _combine_codebase_outputs(
        self, results: List[Any], ruleset_metadata: RepositoryRulesetMetadata
    ) -> str:
        """Combine outputs from all codebases into unified markdown."""
        combined_output = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                codebase_name = ruleset_metadata.codebase_metadata[i].codebase_name
                logger.error("Error processing codebase {}: {}", codebase_name, result)
                combined_output.append(
                    f"### Error processing {codebase_name}\n\n{str(result)}"
                )
            elif isinstance(result, dict) and "output" in result:
                codebase_name = result["codebase_path"]
                output = result["output"]
                combined_output.append(
                    f"### Documentation for `{codebase_name}`\n\n{output}"
                )

        return "\n\n".join(combined_output)

    async def _run_agent_for_codebase(
        self,
        repository_qualified_name: str,
        codebase: CodebaseMetadata,
        request: AgentExecutionRequest,
    ) -> Dict[str, Any]:
        """Run agent for a single codebase (non-streaming)."""
        # Create agent dependencies using app.state
        agent_deps = self._create_agent_dependencies(
            repository_qualified_name, codebase, request
        )

        # Generate user message with codebase-specific context
        # Extract codebase-specific data from the context dictionary
        extra_context = {}
        if request.extra_prompt_context:
            for key, value in request.extra_prompt_context.items():
                if isinstance(value, dict) and codebase.codebase_name in value:
                    # Codebase-specific context: {"project_structure": {"frontend": BaseModel, "backend": BaseModel}}
                    extra_context[key] = value[codebase.codebase_name]
                else:
                    # Global context: {"some_key": BaseModel}
                    extra_context[key] = value

        user_message = self.prompt_provider.get_user_message(
            request.agent_name,
            repository_qualified_name,
            codebase.codebase_name,
            codebase.codebase_path,
            codebase.codebase_programming_language,
            extra_prompt_context=extra_context,
        )

        final_output: Union[BaseModel, List[BaseModel], str, None] = None
        agent_retries = (
            request.agent.retries if hasattr(request.agent, "retries") else None
        )
        codebase_language = codebase.codebase_programming_language

        try:
            result = await request.agent.run(user_message, deps=agent_deps)
            final_output = self._extract_agent_result(result)

        except UnexpectedModelBehavior as e:
            # Enrich context with model/provider info when available
            model_context: Dict[str, Any] = {
                "agent_name": request.agent_name,
                "codebase": codebase.codebase_name,
                "repository": repository_qualified_name,
                "codebase_path": codebase.codebase_path,
                "language": codebase_language,
                "event_namespace": request.event_namespace,
                "agent_retries": agent_retries,
                "prompt_chars": len(user_message)
                if isinstance(user_message, str)
                else None,
            }
            try:
                cfg = await request.fastapi_request.app.state.ai_model_config_service.get_config()  # type: ignore[attr-defined]
                if cfg:
                    model_context.update(
                        {
                            "model_provider": cfg.provider_key,
                            "model_name": cfg.model_name,
                            "provider_name": cfg.provider_name,
                        }
                    )
            except Exception as cfg_err:  # noqa: BLE001
                logger.debug(
                    "Could not fetch model config for error context: {}", cfg_err
                )

            log_agent_error(e, context=model_context, messages=None)
            final_output = f"Agent execution failed: {str(e)}"

        # Optional post-processing
        if request.postprocess_enabled:
            try:
                final_output = await self.post_processing.run(
                    agent_name=request.agent_name,
                    agent_output=final_output or "",
                    repository=repository_qualified_name,
                    codebase=codebase,
                    deps=agent_deps,
                    options=request.postprocess_options,
                )
            except Exception as e:
                logger.warning(
                    "Post-processing failed for {}: {}", request.agent_name, e
                )

        return {"codebase_path": codebase.codebase_name, "output": final_output}

    def _extract_agent_result(
        self, result: Any
    ) -> Union[BaseModel, List[BaseModel], str]:
        """Extract final output from agent result.

        Returns BaseModel, list of BaseModels, or string directly without JSON conversion.
        """
        if result is None:
            return "No result available"

        # Prefer the `output` attribute exposed by pydantic-ai Agent result
        if hasattr(result, "output"):
            payload = result.output
            if isinstance(payload, BaseModel):
                return payload
            if isinstance(payload, list) and all(
                isinstance(x, BaseModel) for x in payload
            ):
                return payload
            if isinstance(payload, str):
                return payload

        # Fallback - convert to string
        return str(result)

    async def _stream_events_for_codebase(
        self,
        repository_qualified_name: str,
        codebase: CodebaseMetadata,
        request: AgentExecutionRequest,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> Union[BaseModel, List[BaseModel], str]:
        """Run streaming agent for a single codebase and push events to queue."""
        event_namespace = request.event_namespace or request.agent_name
        agent_retries = (
            request.agent.retries if hasattr(request.agent, "retries") else None
        )

        # Log model/provider context if available
        try:
            cfg = await request.fastapi_request.app.state.ai_model_config_service.get_config()  # type: ignore[attr-defined]
            if cfg:
                logger.info(
                    "Starting {} for {} using model {}/{} (provider_name={}), retries={}",
                    request.agent_name,
                    codebase.codebase_name,
                    cfg.provider_key,
                    cfg.model_name,
                    cfg.provider_name,
                    agent_retries,
                )
            else:
                logger.debug(
                    "Starting agent {} for codebase {} (no model config)",
                    request.agent_name,
                    codebase.codebase_name,
                )
        except Exception as cfg_err:  # noqa: BLE001
            logger.debug(
                "Starting agent {} for codebase {} (model config unavailable: {})",
                request.agent_name,
                codebase.codebase_name,
                cfg_err,
            )

        # Create agent dependencies using app.state
        agent_deps = self._create_agent_dependencies(
            repository_qualified_name, codebase, request
        )

        # Generate user message with codebase-specific context
        # Extract codebase-specific data from the context dictionary
        extra_context = {}
        if request.extra_prompt_context:
            for key, value in request.extra_prompt_context.items():
                if isinstance(value, dict) and codebase.codebase_name in value:
                    # Codebase-specific context: {"project_structure": {"frontend": BaseModel, "backend": BaseModel}}
                    extra_context[key] = value[codebase.codebase_name]
                else:
                    # Global context: {"some_key": BaseModel}
                    extra_context[key] = value

        user_message = self.prompt_provider.get_user_message(
            request.agent_name,
            repository_qualified_name,
            codebase.codebase_name,
            codebase.codebase_path,
            codebase.codebase_programming_language,
            extra_prompt_context=extra_context,
        )

        final_output: Union[BaseModel, List[BaseModel], str, None] = None
        usage_dict: Optional[Dict[str, int]] = None
        cost_usd: Optional[float] = None

        try:
            try:
                async with request.agent.iter(
                    user_message, deps=agent_deps
                ) as agent_run:
                    async for node in agent_run:
                        await self._process_agent_node(
                            node,
                            agent_run,
                            request,
                            codebase,
                            event_namespace,
                            event_queue,
                        )

                    final_output = self._extract_agent_result(agent_run.result)

                    # Capture usage information
                    run_usage = agent_run.usage()  # Returns RunUsage dataclass
                    usage_dict = asdict(
                        run_usage
                    )  # Convert to dict for JSON serialization

                    # Calculate cost if available
                    if agent_run.result is not None:
                        try:
                            price_calc = agent_run.result.response.cost()
                            cost_usd = float(price_calc.total_price)
                            # Log successful cost calculation
                            logger.info(
                                "Cost estimation successful for {}/{}: ${:.6f} USD (input: ${:.6f}, output: ${:.6f}), model: {}",
                                request.agent_name,
                                codebase.codebase_name,
                                cost_usd,
                                float(price_calc.input_price) if hasattr(price_calc, 'input_price') else 0.0,
                                float(price_calc.output_price) if hasattr(price_calc, 'output_price') else 0.0,
                                agent_run.result.response.model_name if hasattr(agent_run.result.response, 'model_name') else "unknown",
                            )
                        except LookupError:
                            logger.warning(
                                "Cost estimation unavailable for {}/{} - model/provider combination not found in gen-ai-prices database. "
                                "Cost will not be included in statistics. Model: {}",
                                request.agent_name,
                                codebase.codebase_name,
                                agent_run.result.response.model_name if hasattr(agent_run.result.response, 'model_name') else "unknown",
                            )
                        except Exception as exc:  # noqa: BLE001
                            logger.warning(
                                "Unable to calculate cost for {} ({}): {}. Model: {}",
                                request.agent_name,
                                codebase.codebase_name,
                                exc,
                                agent_run.result.response.model_name if hasattr(agent_run.result.response, 'model_name') else "unknown",
                            )

                    logger.info(
                        "Agent {} completed for codebase {} with output: {}",
                        request.agent_name,
                        codebase.codebase_name,
                        final_output,
                    )

                    # Optional post-processing before emitting result
                    processed_output = final_output or ""
                    if request.postprocess_enabled:
                        await event_queue.put(
                            {
                                "event": f"{codebase.codebase_name}:{event_namespace}:postprocess.start",
                                "data": {
                                    "message": "Starting post-processing",
                                    "timestamp": datetime.now().isoformat(),
                                },
                            }
                        )
                        try:
                            processed_output = await self.post_processing.run(
                                agent_name=request.agent_name,
                                agent_output=processed_output,
                                repository=repository_qualified_name,
                                codebase=codebase,
                                deps=agent_deps,
                                options=request.postprocess_options,
                            )
                            await event_queue.put(
                                {
                                    "event": f"{codebase.codebase_name}:{event_namespace}:postprocess.result",
                                    "data": {
                                        "message": "Post-processing complete",
                                        "timestamp": datetime.now().isoformat(),
                                    },
                                }
                            )
                        except Exception as e:
                            logger.warning(
                                "Post-processing failed for {}: {}",
                                request.agent_name,
                                e,
                            )
                            await event_queue.put(
                                {
                                    "event": f"{codebase.codebase_name}:{event_namespace}:postprocess.error",
                                    "data": {
                                        "message": f"Post-processing failed: {str(e)}",
                                        "timestamp": datetime.now().isoformat(),
                                    },
                                }
                            )

                    # Send result event with simple message (BaseModel passed via callback)
                    if processed_output:
                        await event_queue.put(
                            {
                                "event": f"{codebase.codebase_name}:{event_namespace}:result",
                                "data": {
                                    "message": "Analysis complete",
                                    "result": processed_output,  # BaseModel will be handled by callback
                                    "timestamp": datetime.now().isoformat(),
                                },
                            }
                        )

            except UnexpectedModelBehavior as e:
                usage_dict = None
                cost_usd = None
                final_output = await self._handle_agent_error(
                    e,
                    request,
                    codebase,
                    repository_qualified_name,
                    event_namespace,
                    event_queue,
                    None,
                    user_message,
                )

                # Send empty result event for consistency
                await event_queue.put(
                    {
                        "event": f"{codebase.codebase_name}:{event_namespace}:result",
                        "data": {
                            "message": "Analysis failed",
                            "result": "",
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                )
            except Exception as e:
                usage_dict = None
                cost_usd = None
                # Handle any other exception
                logger.error(
                    "Unexpected error in agent {} for codebase {}: {}",
                    request.agent_name,
                    codebase.codebase_name,
                    e,
                )
                await event_queue.put(
                    {
                        "event": f"{codebase.codebase_name}:{event_namespace}:error",
                        "data": {
                            "message": f"Agent execution failed: {str(e)}",
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                )
                final_output = ""

                # Send empty result event for consistency
                await event_queue.put(
                    {
                        "event": f"{codebase.codebase_name}:{event_namespace}:result",
                        "data": {
                            "message": "Analysis failed",
                            "result": "",
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                )

            # Send completion event
            await self._send_completion_event(
                codebase,
                event_namespace,
                request.agent_name,
                event_queue,
                usage_dict=usage_dict,
                cost_usd=cost_usd,
            )

        finally:
            # ALWAYS signal this producer is done, even if an exception occurred
            await event_queue.put({"__done__": True})
            logger.debug(
                "Producer done signal sent for {} - {}",
                request.agent_name,
                codebase.codebase_name,
            )

        return final_output if final_output is not None else ""

    async def _process_agent_node(
        self,
        node: Any,
        agent_run: Any,
        request: AgentExecutionRequest,
        codebase: CodebaseMetadata,
        event_namespace: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Process different types of agent nodes and emit corresponding events."""
        logger.debug(
            "Processing node type: {} for agent {}",
            type(node).__name__,
            request.agent_name,
        )

        if Agent.is_user_prompt_node(node):
            await self._handle_user_prompt_node(
                node, codebase, event_namespace, request.agent_name, event_queue
            )
        elif Agent.is_model_request_node(node):
            await self._handle_model_request_node(
                node,
                agent_run,
                codebase,
                event_namespace,
                request.agent_name,
                event_queue,
            )
        elif Agent.is_call_tools_node(node):
            await self._handle_tool_call_node(
                node, agent_run, request, codebase, event_namespace, event_queue
            )
        elif Agent.is_end_node(node):
            logger.debug(
                "Agent {} reached end node for codebase {}",
                request.agent_name,
                codebase.codebase_name,
            )

    async def _handle_user_prompt_node(
        self,
        node: Any,
        codebase: CodebaseMetadata,
        event_namespace: str,
        agent_name: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Handle user prompt node and emit prompt.start event."""
        prompt_text = str(node.user_prompt) if node.user_prompt else ""
        await event_queue.put(
            {
                "event": f"{codebase.codebase_name}:{event_namespace}:prompt.start",
                "data": {
                    "message": self._get_prompt_start_message(agent_name),
                    "prompt_preview": self._clip_text(prompt_text),
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    async def _handle_model_request_node(
        self,
        node: Any,
        agent_run: Any,
        codebase: CodebaseMetadata,
        event_namespace: str,
        agent_name: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Handle model request node and emit model.request event with streaming support."""
        # Log when entering thinking state
        logger.info(
            "Agent {} entering thinking state for codebase {}",
            agent_name,
            codebase.codebase_name,
        )
        thinking_start = time.time()

        await event_queue.put(
            {
                "event": f"{codebase.codebase_name}:{event_namespace}:model.request",
                "data": {
                    "message": self._get_model_request_message(agent_name),
                    "status": "thinking",
                    "timestamp": datetime.now().isoformat(),
                    "thinking_start": thinking_start,
                },
            }
        )

        # Handle model response streaming if available
        try:
            async with node.stream(agent_run.ctx) as model_stream:
                async for event in model_stream:
                    if isinstance(event, PartDeltaEvent):
                        # Process delta events without logging individual deltas
                        pass
        except Exception as e:
            # Model request nodes may not always support streaming
            logger.error("Model request node streaming not available: {}", e)

    async def _handle_tool_call_node(
        self,
        node: Any,
        agent_run: Any,
        request: AgentExecutionRequest,
        codebase: CodebaseMetadata,
        event_namespace: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Handle tool call node and emit tool.call/tool.result events."""
        async with node.stream(agent_run.ctx) as stream:
            async for event in stream:
                if isinstance(event, FunctionToolCallEvent):
                    await self._emit_tool_call_event(
                        event, request, codebase, event_namespace, event_queue
                    )
                elif isinstance(event, FunctionToolResultEvent):
                    await self._emit_tool_result_event(
                        event, request, codebase, event_namespace, event_queue
                    )

    async def _emit_tool_call_event(
        self,
        event: FunctionToolCallEvent,
        request: AgentExecutionRequest,
        codebase: CodebaseMetadata,
        event_namespace: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Emit tool.call event."""
        tool_name = event.part.tool_name
        args_preview = self._clip_text(str(event.part.args))

        message = self.tool_message_policy.message_for_tool_call(
            request.agent_name, tool_name, args_preview
        )

        await event_queue.put(
            {
                "event": f"{codebase.codebase_name}:{event_namespace}:tool.call",
                "data": {
                    "tool": tool_name,
                    "message": message,
                    "args": args_preview,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    async def _emit_tool_result_event(
        self,
        event: FunctionToolResultEvent,
        request: AgentExecutionRequest,
        codebase: CodebaseMetadata,
        event_namespace: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Emit tool.result event."""
        tool_name = event.result.tool_name if event.result.tool_name else "unknown"
        result_preview = self._clip_text(
            str(event.result.content)
            if hasattr(event.result, "content")
            else "Result received"
        )

        message = self.tool_message_policy.message_for_tool_result(
            request.agent_name, tool_name
        )

        await event_queue.put(
            {
                "event": f"{codebase.codebase_name}:{event_namespace}:tool.result",
                "data": {
                    "tool": tool_name,
                    "message": message,
                    "preview": result_preview,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    async def _handle_agent_error(
        self,
        error: UnexpectedModelBehavior,
        request: AgentExecutionRequest,
        codebase: CodebaseMetadata,
        repository_qualified_name: str,
        event_namespace: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
        messages: List[Any] | None = None,
        user_message: Any | None = None,
    ) -> str:
        """Handle agent execution error and emit error event."""
        # Enrich context with model/provider info when available
        agent_retries = (
            request.agent.retries if hasattr(request.agent, "retries") else None
        )
        codebase_language = codebase.codebase_programming_language
        model_context: Dict[str, Any] = {
            "agent_name": request.agent_name,
            "codebase": codebase.codebase_name,
            "repository": repository_qualified_name,
            "codebase_path": codebase.codebase_path,
            "language": codebase_language,
            "event_namespace": event_namespace,
            "agent_retries": agent_retries,
            "prompt_chars": len(user_message)
            if isinstance(user_message, str)
            else None,
        }
        try:
            cfg = await request.fastapi_request.app.state.ai_model_config_service.get_config()  # type: ignore[attr-defined]
            if cfg:
                model_context.update(
                    {
                        "model_provider": cfg.provider_key,
                        "model_name": cfg.model_name,
                        "provider_name": cfg.provider_name,
                    }
                )
        except Exception as cfg_err:  # noqa: BLE001
            logger.debug("Could not fetch model config for error context: {}", cfg_err)

        log_agent_error(error, context=model_context, messages=messages)

        await event_queue.put(
            {
                "event": f"{codebase.codebase_name}:{event_namespace}:error",
                "data": {
                    "message": f"Agent execution failed: {str(error)}",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

        return f"Agent execution failed: {str(error)}"

    async def _send_completion_event(
        self,
        codebase: CodebaseMetadata,
        event_namespace: str,
        agent_name: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
        usage_dict: Optional[Dict[str, int]] = None,
        cost_usd: Optional[float] = None,
    ) -> None:
        """Send completion event for the codebase."""
        completion_data: Dict[str, Any] = {
            "message": self._get_completion_message(agent_name),
            "codebase": codebase.codebase_name,
            "timestamp": datetime.now().isoformat(),
        }

        # Add usage and cost if available
        if usage_dict:
            completion_data["usage"] = usage_dict
            logger.debug(
                "Adding usage to completion event for {}: requests={}, tokens={}",
                codebase.codebase_name,
                usage_dict.get("requests", 0),
                usage_dict.get("input_tokens", 0) + usage_dict.get("output_tokens", 0),
            )
        if cost_usd is not None:
            completion_data["cost_usd"] = cost_usd
            logger.debug("Adding cost to completion event for {}: ${:.6f}", codebase.codebase_name, cost_usd)
        else:
            logger.debug("No cost data available for completion event for {}", codebase.codebase_name)

        await event_queue.put(
            {
                "event": f"{codebase.codebase_name}:{event_namespace}:complete",
                "data": completion_data,
            }
        )

    def _create_agent_dependencies(
        self,
        repository_qualified_name: str,
        codebase: CodebaseMetadata,
        request: AgentExecutionRequest,
    ) -> AgentDependencies:
        """Create agent dependencies using FastAPI app.state."""
        return AgentDependencies(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase,
            neo4j_conn_manager=request.fastapi_request.app.state.neo4j_manager,
            context7_agent=request.fastapi_request.app.state.agents["context7_agent"],
            library_documentation_service=LibraryDocumentationService(),
        )

    def _get_prompt_start_message(self, agent_name: str) -> str:
        """Get agent-specific prompt start message."""
        messages = {
            "framework_explorer": "Analyzing major frameworks and libraries...",
            "project_configuration_agent": "Analyzing project structure...",
            "development_workflow": "Analyzing development workflow (build/test/lint/type-check)...",
            "business_logic_domain": "Analyzing business logic domains...",
        }
        return messages.get(agent_name, f"Starting {agent_name} analysis...")

    def _get_model_request_message(self, agent_name: str) -> str:
        """Get agent-specific model request message."""
        messages = {
            "framework_explorer": "Agent is analyzing frameworks and libraries...",
            "project_configuration_agent": "Agent is analyzing project structure...",
            "development_workflow": "Agent is deriving build, dev, test, lint, and type-check commands...",
            "business_logic_domain": "Agent is grouping core files into business domains...",
        }
        return messages.get(agent_name, f"Agent is processing {agent_name}...")

    def _get_completion_message(self, agent_name: str) -> str:
        """Get agent-specific completion message."""
        messages = {
            "framework_explorer": "🎉 Major frameworks analysis complete for codebase",
            "project_configuration_agent": "🎉 Project structure analysis complete for codebase",
            "development_workflow": "🎉 Development workflow analysis complete for codebase",
            "business_logic_domain": "🎉 Business logic domain analysis complete for codebase",
        }
        return messages.get(
            agent_name, f"🎉 {agent_name} analysis complete for codebase"
        )

    def _clip_text(self, text: str, max_length: int = 300) -> str:
        """Clip text to maximum length with ellipsis if truncated.

        Args:
            text: Text to clip
            max_length: Maximum allowed length (default 300)

        Returns:
            Clipped text with ellipsis if truncated
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
