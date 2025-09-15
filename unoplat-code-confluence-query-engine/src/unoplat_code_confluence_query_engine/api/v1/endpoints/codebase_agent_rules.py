import asyncio
from functools import partial
import json
import time
from typing import AsyncGenerator, Awaitable, Callable, Dict, Optional, Union
import uuid

from fastapi import APIRouter, HTTPException, Query, Request
from loguru import logger
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from unoplat_code_confluence_query_engine.db.repository_metadata_service import (
    fetch_repository_metadata,
)
from unoplat_code_confluence_query_engine.models.agent_execution_request import (
    AgentExecutionRequest,
)
from unoplat_code_confluence_query_engine.models.agent_md_aggregate import (
    AgentMdAggregate,
)
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    BusinessLogicDomain,
    DevelopmentWorkflow,
    ProgrammingLanguageMetadataOutput,
    ProjectConfiguration,
)
from unoplat_code_confluence_query_engine.models.repository_ruleset_metadata import (
    RepositoryRulesetMetadata,
)
from unoplat_code_confluence_query_engine.services.agent_execution_service import (
    AgentExecutionService,
)
from unoplat_code_confluence_query_engine.services.package_manager_metadata_service import (
    fetch_programming_language_metadata,
)

router = APIRouter(prefix="/v1", tags=["codebase-rules"])


def log_sse_event(connection_id: str, event_count: int, event_type: str, 
                  connection_start: float, last_event_time: float) -> float:
    """Log SSE event details for debugging timeout issues."""
    current_time = time.time()
    time_since_last = current_time - last_event_time
    time_since_start = current_time - connection_start
    
    logger.debug(
        "SSE[{}] Event #{}: type={}, time_since_last={:.2f}s, total_time={:.2f}s",
        connection_id, event_count, event_type, time_since_last, time_since_start
    )
    
    # Warn if too much time between events
    if time_since_last > 15:
        logger.warning(
            "SSE[{}] Long gap detected: {:.2f}s since last event",
            connection_id, time_since_last
        )
    
    return current_time


async def _update_directory_result(
    aggregators: Dict[str, AgentMdAggregate],
    project_structure_by_codebase: Dict[str, ProjectConfiguration],
    codebase_name: str,
    result: ProjectConfiguration,
) -> None:
    """Update directory agent result in aggregator and project structure cache."""
    project_structure_by_codebase[codebase_name] = result
    aggregators[codebase_name].update_from_project_configuration_agent(result)


# async def _update_framework_result(
#     aggregators: Dict[str, AgentMdAggregate],
#     codebase_name: str,
#     result: list[FrameworkLibraryOutput],
# ) -> None:
#     """Update framework explorer result in aggregator."""
#     aggregators[codebase_name].update_from_framework_explorer(result)


# async def _update_framework_result_with_baseline(
#     aggregators: Dict[str, AgentMdAggregate],
#     neo4j_manager: CodeConfluenceGraphQueryEngine,
#     codebase_name: str,
#     result: list[FrameworkLibraryOutput],
# ) -> None:
#     """Merge baseline (KG) frameworks with agent novel frameworks and update aggregator.

#     - Prefer baseline entries when names overlap.
#     - Append only novel items not present in baseline (case-insensitive by name).
#     """
#     aggregator = aggregators[codebase_name]

#     # Fetch baseline frameworks for this codebase
#     baseline = await fetch_baseline_frameworks_as_outputs(
#         neo4j_manager, aggregator.codebase.codebase_path, aggregator.codebase.codebase_programming_language
#     )

#     baseline_map = {i.name.strip().lower(): i for i in baseline}

#     merged: list[FrameworkLibraryOutput] = list(baseline_map.values())

#     added_novel = 0
#     for item in result:
#         key = item.name.strip().lower()
#         if key in baseline_map:
#             continue
#         merged.append(item)
#         added_novel += 1

#     aggregators[codebase_name].update_from_framework_explorer(merged)
#     logger.debug(
#         "Framework merge for {}: baseline={}, novel_added={}, merged_total={}",
#         codebase_name,
#         len(baseline),
#         added_novel,
#         len(merged),
#     )


async def _update_workflow_result(
    aggregators: Dict[str, AgentMdAggregate],
    codebase_name: str,
    result: DevelopmentWorkflow,
) -> None:
    """Update development workflow result in aggregator."""
    aggregators[codebase_name].update_from_development_workflow(result)


async def _update_business_logic_result(
    aggregators: Dict[str, AgentMdAggregate],
    codebase_name: str,
    result: BusinessLogicDomain,
) -> None:
    """Update business logic result in aggregator."""
    aggregators[codebase_name].update_from_business_logic(result)


async def _stream_agent(
    request: Request,
    service: AgentExecutionService,
    ruleset_metadata: RepositoryRulesetMetadata,
    exec_request: AgentExecutionRequest,
    *,
    on_result: Optional[Callable[[str, Union[BaseModel, list[BaseModel], str]], Awaitable[None]]] = None,
) -> AsyncGenerator[Dict[str, str], None]:
    """Yield pass-through SSE events; call on_result(codebase_name, result_model) when result arrives.
    
    Args:
        request: FastAPI request object for connection monitoring
        service: Agent execution service
        ruleset_metadata: Repository ruleset metadata
        exec_request: Agent execution request
        on_result: Optional callback for when result events arrive with BaseModel
        
    Yields:
        SSE events to forward to the client
    """
    async for progress_event in service.run_stream(ruleset_metadata, request=exec_request):
        # Check for client disconnection
        if await request.is_disconnected():
            break
        
        # Handle result events
        if on_result and progress_event["event"].endswith(f":{exec_request.event_namespace or exec_request.agent_name}:result"):
            codebase_name = progress_event["event"].split(":")[0]
            result_data = progress_event["data"].get("result")
            if result_data is not None:
                await on_result(codebase_name, result_data)
                # Remove BaseModel from event data to avoid JSON serialization issues
                # The BaseModel has been passed to the callback, so we don't need it in the SSE event
                progress_event = {
                    "event": progress_event["event"],
                    "data": {k: v for k, v in progress_event["data"].items() if k != "result"}
                }
        
        # Yield event to client (without BaseModel in data)
        yield progress_event


async def generate_sse_events(
    request: Request,
    ruleset_metadata: RepositoryRulesetMetadata,
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Generate SSE events for streaming agent response with real-time progress and final aggregation.

    This generator:
    1. Sends initial status event
    2. Pre-fetches language metadata for all codebases
    3. Initializes aggregators for each codebase
    4. Streams all four agents in sequence with aggregation
    5. Emits final repository-level AgentMdOutput event
    6. Enhanced with connection monitoring and timeout handling

    Args:
        request: FastAPI request object for connection monitoring
        ruleset_metadata: Validated repository ruleset metadata

    Yields:
        Dictionary events for SSE streaming with final aggregated output
    """
    # Initialize debug tracking
    connection_id = str(uuid.uuid4())[:8]
    connection_start = time.time()
    event_count = 0
    last_event_time = time.time()
    
    logger.info("SSE connection started: id={}, repo={}", 
               connection_id, ruleset_metadata.repository_qualified_name)
    
    try:
        event_id = 0

        # Send initial status event
        initial_event = {
            "event": "status",
            "data": json.dumps(
                {
                    "message": "Initializing agent aggregation...",
                    "repository": ruleset_metadata.repository_qualified_name,
                },
                ensure_ascii=False,
            ),
            "id": str(event_id),
        }
        last_event_time = log_sse_event(connection_id, event_count, "status", connection_start, last_event_time)
        event_count += 1
        yield initial_event
        event_id += 1
        
        # Initialize unified agent execution service (logs at project-root/logs/agent_runs)
        agent_execution_service = AgentExecutionService()

        # Initialize per-codebase aggregators
        aggregators: Dict[str, AgentMdAggregate] = {}
        project_structure_by_codebase: Dict[str, ProjectConfiguration] = {}
        
        # Pre-fetch programming language metadata for all codebases
        for codebase in ruleset_metadata.codebase_metadata:
            aggregator = AgentMdAggregate(codebase)
            # Use underscore-based qualified name for Neo4j lookups (owner_repo convention)
            underscore_qualified = ruleset_metadata.repository_qualified_name.replace("/", "_")
            language_metadata: Optional[ProgrammingLanguageMetadataOutput] = await fetch_programming_language_metadata(
                request.app.state.neo4j_manager,
                underscore_qualified,
                codebase.codebase_path,
            )
            aggregator.set_language_metadata(language_metadata)
            aggregators[codebase.codebase_name] = aggregator
        
        
        # Log current agent registry state for debugging
        try:
            available_agents = list(request.app.state.agents.keys())  # type: ignore[attr-defined]
        except Exception:
            available_agents = []
        logger.debug("SSE[{}] Available agents at request time: {}", connection_id, available_agents)

        # Stream project structure analysis events using project_configuration_agent
        if "project_configuration_agent" not in available_agents:
            logger.error(
                "SSE[{}] Missing 'project_configuration_agent' in app.state.agents. Available: {}",
                connection_id,
                available_agents,
            )
            raise RuntimeError("Agents not initialized or missing 'project_configuration_agent'")

        project_configuration_request = AgentExecutionRequest(
            agent_name="project_configuration_agent",
            agent=request.app.state.agents['project_configuration_agent'],
            fastapi_request=request,
            event_namespace="project_configuration_agent"
        )
        
        directory_result_handler = partial(
            _update_directory_result, aggregators, project_structure_by_codebase
        )
        
        async for progress_event in _stream_agent(
            request, agent_execution_service, ruleset_metadata, project_configuration_request,
            on_result=directory_result_handler
        ):
            sse_event = {
                "event": progress_event["event"],
                "data": json.dumps(progress_event["data"], ensure_ascii=False),
                "id": str(event_id),
            }
            last_event_time = log_sse_event(connection_id, event_count, progress_event["event"], connection_start, last_event_time)
            event_count += 1
            yield sse_event
            event_id += 1

        # TODO: modify this later
        # framework_request = AgentExecutionRequest(
        #     agent_name="framework_explorer",
        #     agent=request.app.state.agents['framework_explorer_agent'], 
        #     fastapi_request=request,
        #     event_namespace="framework_explorer",
        #     postprocess_enabled=True,
        # )
        
        # # Merge baseline (KG) ∪ novel (agent) per codebase
        # framework_result_handler = partial(
        #     _update_framework_result_with_baseline,
        #     aggregators,
        #     request.app.state.neo4j_manager,
        # )
        
        # async for progress_event in _stream_agent(
        #     request, agent_execution_service, ruleset_metadata, framework_request,
        #     on_result=framework_result_handler
        # ):
        #     sse_event = {
        #         "event": progress_event["event"],
        #         "data": json.dumps(progress_event["data"]),
        #         "id": str(event_id),
        #     }
        #     last_event_time = log_sse_event(connection_id, event_count, progress_event["event"], connection_start, last_event_time)
        #     event_count += 1
        #     yield sse_event
        #     event_id += 1

        # Stream development workflow analysis events using development_workflow_agent
        development_request = AgentExecutionRequest(
            agent_name="development_workflow",
            agent=request.app.state.agents['development_workflow_agent'],
            fastapi_request=request,
            event_namespace="development_workflow",
            extra_prompt_context={"project_structure": project_structure_by_codebase}
        )
        
        workflow_result_handler = partial(_update_workflow_result, aggregators)
        
        async for progress_event in _stream_agent(
            request, agent_execution_service, ruleset_metadata, development_request,
            on_result=workflow_result_handler
        ):
            sse_event = {
                "event": progress_event["event"],
                "data": json.dumps(progress_event["data"]),
                "id": str(event_id),
            }
            last_event_time = log_sse_event(connection_id, event_count, progress_event["event"], connection_start, last_event_time)
            event_count += 1
            yield sse_event
            event_id += 1

        # Stream business logic domain analysis events using business_logic_domain_agent
        business_logic_request = AgentExecutionRequest(
            agent_name="business_logic_domain",
            agent=request.app.state.agents['business_logic_domain_agent'],
            fastapi_request=request,
            event_namespace="business_logic_domain",
            postprocess_enabled=True,
        )

        business_logic_result_handler = partial(_update_business_logic_result, aggregators)
        
        async for progress_event in _stream_agent(
            request, agent_execution_service, ruleset_metadata, business_logic_request,
            on_result=business_logic_result_handler
        ):
            sse_event = {
                "event": progress_event["event"],
                "data": json.dumps(progress_event["data"]),
                "id": str(event_id),
            }
            last_event_time = log_sse_event(connection_id, event_count, progress_event["event"], connection_start, last_event_time)
            event_count += 1
            yield sse_event
            event_id += 1

        # # Check for disconnection before final event
        if await request.is_disconnected():
            duration = time.time() - connection_start
            logger.info("SSE[{}] Client disconnected before final event after {:.2f}s", connection_id, duration)
            return

        # Build final repository payload
        final_payload: Dict[str, str | Dict[str, object]] = {
            "repository": ruleset_metadata.repository_qualified_name,
            "codebases": {}
        }
        
        for codebase_name, aggregator in aggregators.items():
            final_model = aggregator.to_final_model()
            # Exclude optional fields that are None to avoid nulls in SSE payload
            final_payload["codebases"][codebase_name] = final_model.model_dump(exclude_none=True)  # type: ignore
        
        # Emit final repository-level event
        final_event = {
            "event": "final:agent_md_output",
            "data": json.dumps(final_payload, ensure_ascii=False),
            "id": str(event_id),
        }
        last_event_time = log_sse_event(connection_id, event_count, "final:agent_md_output", connection_start, last_event_time)
        event_count += 1
        yield final_event
        
        logger.info("SSE[{}] Final aggregated event emitted for {} codebases", 
                   connection_id, len(aggregators))

    except asyncio.CancelledError:
        # Enhanced: Better cancellation handling for sse-starlette 3.0.2
        duration = time.time() - connection_start
        logger.info("SSE[{}] Connection cancelled after {:.2f}s, {} events sent",
                   connection_id, duration, event_count)
        yield {
            "event": "error",
            "data": json.dumps({"message": "Connection cancelled"}, ensure_ascii=False),
            "id": str(event_id),
        }
        raise
    except Exception as e:
        duration = time.time() - connection_start
        logger.error("SSE[{}] Connection error after {:.2f}s: {}",
                    connection_id, duration, e)
        yield {
            "event": "error",
            "data": json.dumps({"error": str(e)}, ensure_ascii=False),
            "id": str(event_id),
        }


@router.get("/codebase-agent-rules")
async def get_codebase_agent_rules(
    request: Request,
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
) -> EventSourceResponse:
    """
    Stream codebase agent rules via Server-Sent Events using pydantic-ai agent.

    This endpoint:
    1. Fetches repository and codebase configuration from PostgreSQL
    2. Builds RepositoryRulesetMetadata from database data
    3. Invokes the pydantic-ai agent with real-time streaming via agent.iter()
    4. Streams the agent's AGENTS.md content generation with live progress

    Enhanced features:
    - Connection monitoring with automatic disconnection detection
    - Enhanced timeout handling
    - Better error handling and recovery
    - Real-time progress updates via agent.iter() nodes
    - Direct database integration instead of encoded parameters

    Args:
        request: FastAPI request object for connection monitoring
        owner_name: Repository owner name
        repo_name: Repository name

    Returns:
        EventSourceResponse streaming AGENTS.md content generation with real-time progress
    """
    try:
        # Fetch repository metadata from PostgreSQL and resolve absolute paths from Neo4j
        ruleset_metadata = await fetch_repository_metadata(
            owner_name, repo_name, request.app.state.neo4j_manager
        )
        logger.info("Fetched repository metadata: {}", ruleset_metadata)


        # Return EventSourceResponse with enhanced timeout and error handling (sse-starlette 3.0.2)
        return EventSourceResponse(
            generate_sse_events(request, ruleset_metadata),
            ping=10,  # Send keepalive ping every 10 seconds
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering for real-time streaming
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in get_codebase_agent_rules: {}", e)
        raise HTTPException(status_code=500, detail="Internal server error")
