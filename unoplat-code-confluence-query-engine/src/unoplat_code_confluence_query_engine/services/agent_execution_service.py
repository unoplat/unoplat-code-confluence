"""Unified agent execution service consolidating duplicated logic."""

import asyncio
from datetime import datetime
from pathlib import Path
import time
from typing import Any, AsyncGenerator, Dict, List, Union

from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
)

from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.models.agent_execution_request import (
    AgentExecutionRequest,
)

# NOTE: Keep model imports minimal to avoid unused warnings; AgentMdOutput not needed here.
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
from unoplat_code_confluence_query_engine.services.post_processing_service import (
    PostProcessingService,
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
    save_nodes_to_json,
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
                        logger.debug("Producer completed, {} remaining", producers_remaining)
                        continue  # Don't yield the done signal itself
                    
                    yield event
                    
                except asyncio.TimeoutError:
                    # Log timeout but continue
                    if queue_wait_start:
                        wait_time = time.time() - queue_wait_start
                        logger.trace("Queue timeout after {:.2f}s (normal during processing)", wait_time)
                    continue
            
            logger.debug("All producers complete: total_waits={}, max_wait={:.2f}s",
                        total_queue_waits, max_queue_wait)
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
        self, 
        results: List[Any], 
        ruleset_metadata: RepositoryRulesetMetadata
    ) -> str:
        """Combine outputs from all codebases into unified markdown."""
        combined_output = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                codebase_name = ruleset_metadata.codebase_metadata[i].codebase_name
                logger.error("Error processing codebase {}: {}", codebase_name, result)
                combined_output.append(f"### Error processing {codebase_name}\n\n{str(result)}")
            elif isinstance(result, dict) and "output" in result:
                codebase_name = result["codebase_path"]
                output = result["output"]
                combined_output.append(f"### Documentation for `{codebase_name}`\n\n{output}")
        
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
        
        nodes: List[Any] = []
        final_output: Union[BaseModel, List[BaseModel], str, None] = None
        
        try:
            async with request.agent.iter(user_message, deps=agent_deps) as agent_run:
                async for node in agent_run:
                    nodes.append(node)
                
                final_output = self._extract_agent_result(agent_run.result)
        
        except UnexpectedModelBehavior as e:
            log_agent_error(
                e,
                context={
                    "agent_name": request.agent_name,
                    "codebase": codebase.codebase_name,
                    "repository": repository_qualified_name,
                },
            )
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
                logger.warning("Post-processing failed for {}: {}", request.agent_name, e)

        # Save execution nodes
        await save_nodes_to_json(
            self.logs_dir,
            filename_prefix=(
                f"agent_run_{request.agent_name}_"
                f"{repository_qualified_name}_{codebase.codebase_name.replace('/', '_')}"
            ),
            nodes=nodes,
        )
        
        return {"codebase_path": codebase.codebase_name, "output": final_output}
    
    def _extract_agent_result(self, result: Any) -> Union[BaseModel, List[BaseModel], str]:
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
            if isinstance(payload, list) and all(isinstance(x, BaseModel) for x in payload):
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
        
        logger.debug("Starting agent {} for codebase {}", request.agent_name, codebase.codebase_name)
        
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
        
        nodes: List[Any] = []
        final_output: Union[BaseModel, List[BaseModel], str, None] = None
        
        try:
            try:
                async with request.agent.iter(user_message, deps=agent_deps) as agent_run:
                    async for node in agent_run:
                        nodes.append(node)
                        await self._process_agent_node(
                            node, agent_run, request, codebase, event_namespace, event_queue
                        )
                    
                    final_output = self._extract_agent_result(agent_run.result)
                    
                    logger.info("Agent {} completed for codebase {} with output: {}", request.agent_name, codebase.codebase_name, final_output)
                    
                    # Optional post-processing before emitting result
                    processed_output = final_output or ""
                    if request.postprocess_enabled:
                        await event_queue.put({
                            "event": f"{codebase.codebase_name}:{event_namespace}:postprocess.start",
                            "data": {
                                "message": "Starting post-processing",
                                "timestamp": datetime.now().isoformat(),
                            },
                        })
                        try:
                            processed_output = await self.post_processing.run(
                                agent_name=request.agent_name,
                                agent_output=processed_output,
                                repository=repository_qualified_name,
                                codebase=codebase,
                                deps=agent_deps,
                                options=request.postprocess_options,
                            )
                            await event_queue.put({
                                "event": f"{codebase.codebase_name}:{event_namespace}:postprocess.result",
                                "data": {
                                    "message": "Post-processing complete",
                                    "timestamp": datetime.now().isoformat(),
                                },
                            })
                        except Exception as e:
                            logger.warning("Post-processing failed for {}: {}", request.agent_name, e)
                            await event_queue.put({
                                "event": f"{codebase.codebase_name}:{event_namespace}:postprocess.error",
                                "data": {
                                    "message": f"Post-processing failed: {str(e)}",
                                    "timestamp": datetime.now().isoformat(),
                                },
                            })

                    # Send result event with simple message (BaseModel passed via callback)
                    if processed_output:
                        await event_queue.put({
                            "event": f"{codebase.codebase_name}:{event_namespace}:result",
                            "data": {
                                "message": "Analysis complete",
                                "result": processed_output,  # BaseModel will be handled by callback
                                "timestamp": datetime.now().isoformat(),
                            },
                        })
            
            except UnexpectedModelBehavior as e:
                final_output = await self._handle_agent_error(
                    e, request, codebase, repository_qualified_name, event_namespace, event_queue
                )
                
                # Send empty result event for consistency
                await event_queue.put({
                    "event": f"{codebase.codebase_name}:{event_namespace}:result",
                    "data": {
                        "message": "Analysis failed",
                        "result": "",
                        "timestamp": datetime.now().isoformat(),
                    },
                })
            except Exception as e:
                # Handle any other exception
                logger.error("Unexpected error in agent {} for codebase {}: {}", 
                            request.agent_name, codebase.codebase_name, e)
                await event_queue.put({
                    "event": f"{codebase.codebase_name}:{event_namespace}:error",
                    "data": {
                        "message": f"Agent execution failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    },
                })
                final_output = ""
                
                # Send empty result event for consistency
                await event_queue.put({
                    "event": f"{codebase.codebase_name}:{event_namespace}:result",
                    "data": {
                        "message": "Analysis failed",
                        "result": "",
                        "timestamp": datetime.now().isoformat(),
                    },
                })
            
            # Save execution nodes
            await save_nodes_to_json(
                self.logs_dir,
                filename_prefix=(
                    f"agent_run_{request.agent_name}_"
                    f"{repository_qualified_name}_{codebase.codebase_name.replace('/', '_')}"
                ),
                nodes=nodes,
            )
            
            # Send completion event
            await self._send_completion_event(codebase, event_namespace, request.agent_name, event_queue)
            
        finally:
            # ALWAYS signal this producer is done, even if an exception occurred
            await event_queue.put({"__done__": True})
            logger.debug("Producer done signal sent for {} - {}", request.agent_name, codebase.codebase_name)
        
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
        logger.debug("Processing node type: {} for agent {}", type(node).__name__, request.agent_name)
        
        if Agent.is_user_prompt_node(node):
            await self._handle_user_prompt_node(node, codebase, event_namespace, request.agent_name, event_queue)
        elif Agent.is_model_request_node(node):
            await self._handle_model_request_node(node, agent_run, codebase, event_namespace, request.agent_name, event_queue)
        elif Agent.is_call_tools_node(node):
            await self._handle_tool_call_node(node, agent_run, request, codebase, event_namespace, event_queue)
        elif Agent.is_end_node(node):
            logger.debug("Agent {} reached end node for codebase {}", request.agent_name, codebase.codebase_name)
    
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
        await event_queue.put({
            "event": f"{codebase.codebase_name}:{event_namespace}:prompt.start",
            "data": {
                "message": self._get_prompt_start_message(agent_name),
                "prompt_preview": prompt_text[:200] if len(prompt_text) > 200 else prompt_text,
                "timestamp": datetime.now().isoformat(),
            },
        })
    
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
        logger.info("Agent {} entering thinking state for codebase {}", 
                   agent_name, codebase.codebase_name)
        thinking_start = time.time()
        
        await event_queue.put({
            "event": f"{codebase.codebase_name}:{event_namespace}:model.request",
            "data": {
                "message": self._get_model_request_message(agent_name),
                "status": "thinking",
                "timestamp": datetime.now().isoformat(),
                "thinking_start": thinking_start,
            },
        })
        
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
        args_preview = str(event.part.args)
        
        message = self.tool_message_policy.message_for_tool_call(
            request.agent_name, tool_name, args_preview
        )
        
        await event_queue.put({
            "event": f"{codebase.codebase_name}:{event_namespace}:tool.call",
            "data": {
                "tool": tool_name,
                "message": message,
                "args": args_preview,
                "timestamp": datetime.now().isoformat(),
            },
        })
    
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
        result_preview = (
            str(event.result.content)
            if hasattr(event.result, "content")
            else "Result received"
        )
        
        message = self.tool_message_policy.message_for_tool_result(
            request.agent_name, tool_name
        )
        
        await event_queue.put({
            "event": f"{codebase.codebase_name}:{event_namespace}:tool.result",
            "data": {
                "tool": tool_name,
                "message": message,
                "preview": result_preview,
                "timestamp": datetime.now().isoformat(),
            },
        })
    
    async def _handle_agent_error(
        self,
        error: UnexpectedModelBehavior,
        request: AgentExecutionRequest,
        codebase: CodebaseMetadata,
        repository_qualified_name: str,
        event_namespace: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> str:
        """Handle agent execution error and emit error event."""
        log_agent_error(
            error,
            context={
                "agent_name": request.agent_name,
                "codebase": codebase.codebase_name,
                "repository": repository_qualified_name,
            },
        )
        
        await event_queue.put({
            "event": f"{codebase.codebase_name}:{event_namespace}:error",
            "data": {
                "message": f"Agent execution failed: {str(error)}",
                "timestamp": datetime.now().isoformat(),
            },
        })
        
        return f"Agent execution failed: {str(error)}"
    
    async def _send_completion_event(
        self,
        codebase: CodebaseMetadata,
        event_namespace: str,
        agent_name: str,
        event_queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Send completion event for the codebase."""
        await event_queue.put({
            "event": f"{codebase.codebase_name}:{event_namespace}:complete",
            "data": {
                "message": self._get_completion_message(agent_name),
                "codebase": codebase.codebase_name,
                "timestamp": datetime.now().isoformat(),
            },
        })
    
    def _create_agent_dependencies(
        self, 
        repository_qualified_name: str, 
        codebase: CodebaseMetadata, 
        request: AgentExecutionRequest
    ) -> AgentDependencies:
        """Create agent dependencies using FastAPI app.state."""
        return AgentDependencies(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase,
            neo4j_conn_manager=request.fastapi_request.app.state.neo4j_manager,
            context7_agent=request.fastapi_request.app.state.agents['context7_agent'],
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
        return messages.get(agent_name, f"🎉 {agent_name} analysis complete for codebase")
