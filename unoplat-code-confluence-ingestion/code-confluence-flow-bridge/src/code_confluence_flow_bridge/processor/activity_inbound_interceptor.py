from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.github.github_repo import JobStatus
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import CodebaseWorkflowDbActivityEnvelope, ParentWorkflowDbActivityEnvelope
from src.code_confluence_flow_bridge.processor.db.postgres.child_workflow_db_activity import ChildWorkflowDbActivity
from src.code_confluence_flow_bridge.processor.db.postgres.parent_workflow_db_activity import ParentWorkflowDbActivity

import json
from typing import Any, Dict, List, cast

from temporalio import activity
from temporalio.activity import Info
from temporalio.exceptions import ApplicationError
from temporalio.worker import ActivityInboundInterceptor, ExecuteActivityInput, Interceptor


class ActivityStatusInterceptor(Interceptor):
    """Worker interceptor to update activity status (RUNNING/RETRYING) in the DB."""

    def intercept_activity(self, next: ActivityInboundInterceptor) -> ActivityInboundInterceptor:
        return ActivityStatusInboundInterceptor(next)


class ActivityStatusInboundInterceptor(ActivityInboundInterceptor):
    """Inbound interceptor for activities to mark RUNNING/RETRYING status."""

    def __init__(self, next: ActivityInboundInterceptor) -> None:
        self.parent_db_activity = ParentWorkflowDbActivity()
        self.child_db_activity = ChildWorkflowDbActivity()
        super().__init__(next)

    async def execute_activity(self, input: ExecuteActivityInput) -> Any:
        
        log = seed_and_bind_logger_from_trace_id()
        log.debug("Inside Activity Status Inbound Interceptor")
        # Get activity info
        info: Info = activity.info()
        
        # Extract contextual info
        activity_id = info.activity_id
        activity_type = info.activity_type
        # attempt is only used in the exception handler for RETRYING status
        workflow_id = info.workflow_id
        workflow_run_id = info.workflow_run_id
        workflow_type = info.workflow_type
        
        # Skip certain activities (like the status update activity itself)
        if activity_type in ["update-repository-workflow-status", "update-codebase-workflow-status"]:
            return await self.next.execute_activity(input)
        
        # Initialize variables
        trace_id: str 
        repository_name: str 
        repository_owner_name: str
        parent_workflow_run_id: str
        
        # Extract information from headers
        try:
            # Extract trace_id from headers
            if "trace_id" in input.headers:
                trace_id_payload = input.headers["trace_id"]
                trace_id = trace_id_payload.data.decode('utf-8')
            
            # Try to extract repository name and owner directly from headers first
            if "repository_name" in input.headers:
                repository_name = input.headers["repository_name"].data.decode('utf-8')
            
            if "repository_owner_name" in input.headers:
                repository_owner_name = input.headers["repository_owner_name"].data.decode('utf-8')
            
            
            log.debug(f"Extracted repository name from headers inside activity interceptor: {repository_name}")
            log.debug(f"Extracted repository owner name from headers inside activity interceptor: {repository_owner_name}")
            
            # Extract parent_workflow_run_id from headers
            if "parent_workflow_run_id" in input.headers:
                parent_workflow_run_id_payload = input.headers["parent_workflow_run_id"]
                parent_workflow_run_id = parent_workflow_run_id_payload.data.decode('utf-8')
                log.debug(f"Extracted parent_workflow_run_id from headers: {parent_workflow_run_id}")
            
            # Extract and parse codebase configs from headers
            codebase_configs: List[Dict[str, Any]] = []
            if "codebases" in input.headers:
                codebases_payload = input.headers["codebases"]
                codebase_configs = json.loads(codebases_payload.data.decode('utf-8'))
                log.debug(f"Extracted codebase configs from headers: {codebase_configs}")
        except Exception as e:
            # We'll set up a basic logger below
            log.error(f"Failed to extract contextual information from headers: {str(e)}")
            raise e
        
        # Set up logger with available context early in the method
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id or "unknown",
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            activity_id=activity_id,
            activity_name=activity_type
        )
        
        # Log extracted context for debugging
        log.debug(f"Activity context: trace_id={trace_id}, repo={repository_name}/{repository_owner_name}, "
                 f"workflow_type={workflow_type}, activity_type={activity_type}")
        
        # If essential values weren't found, log warning but continue
        if not (trace_id and repository_name and repository_owner_name):
            log.warning("Missing essential context from headers. Status updates may be incomplete.")
            # Continue with execution - we'll do our best with what we have
        
        # We're removing the RUNNING state update logic here, as requested
        # Only the RETRYING logic in the exception handler below will be kept
        log.debug(f"Skipping RUNNING state update for activity {activity_type} as it's now handled by the workflow interceptor")

        # Execute the activity
        try:
            result = await self.next.execute_activity(input)
            # No need to mark success here - the existing workflow interceptor already marks COMPLETED
            return result
        except Exception as e:
            # Update status to RETRYING when an exception occurs
            error_report = None
            
            # Get attempt count - only set to RETRYING if this is a retry attempt
            attempt = info.attempt
            status_to_mark = JobStatus.RETRYING if attempt > 1 else JobStatus.FAILED
            log.error(f"Activity {activity_type} failed (attempt {attempt}): {str(e)}")
            
            # Try to update status to FAILED in database
            try:
                # Handle parent workflow (repo-activity-workflow) status updates
                if workflow_type == "repo-activity-workflow":
                    log.debug(
                        "Processing error for repo-activity-workflow | repository={}/{} | workflow_id={} | error_type={}",
                        repository_name, repository_owner_name, workflow_id, type(e).__name__
                    )
                    if repository_name and repository_owner_name and workflow_id and workflow_run_id:
                        log.debug(
                            "All required parameters present for error update | repository={}/{} | workflow_id={}",
                            repository_name, repository_owner_name, workflow_id
                        )
                        # Ensure trace_id is not None before using it
                        if trace_id is None:
                            # Both repository_name and repository_owner_name must be strings at this point
                            assert repository_name is not None and repository_owner_name is not None, "Repository name and owner must be defined"
                            trace_id = f"{repository_name}__{repository_owner_name}"  # Fallback if trace_id is missing
                        
                        # Use cast to tell type checker that trace_id is definitely a string at this point
                        safe_trace_id = cast(str, trace_id)
                        
                        parent_env = ParentWorkflowDbActivityEnvelope(
                            repository_name=repository_name,
                            repository_owner_name=repository_owner_name,
                            workflow_id=workflow_id,
                            workflow_run_id=workflow_run_id,
                            trace_id=safe_trace_id,
                            status=status_to_mark.value,
                            repository_metadata=[],
                            error_report=error_report
                        )
                        
                        # Directly call the activity method instead of using workflow.execute_activity
                        await self.parent_db_activity.update_repository_workflow_status(parent_env)
                
                # Handle child workflow (child-codebase-workflow) status updates
                elif workflow_type == "child-codebase-workflow":
                    log.debug(
                        "Processing error for child-codebase-workflow | repository={}/{} | workflow_id={} | error_type={}",
                        repository_name, repository_owner_name, workflow_id, type(e).__name__
                    )
                    
                    # Extract root package from the workflow_id
                    # Pattern: codebase-child-workflow_{codebase_qualified_name}_{root_package}
                    target_root_package = None
                    try:
                        if workflow_id.startswith("codebase-child-workflow_"):
                            # Split by underscore and get the last element
                            workflow_id_parts = workflow_id.split('|')
                            if len(workflow_id_parts) > 2:  # Ensure we have enough parts
                                target_root_package = workflow_id_parts[-1]
                                log.debug(
                                    "Extracted root package from workflow_id: {} -> {}",
                                    workflow_id, target_root_package
                                )
                    except Exception as parse_error:
                        log.error(
                            "Failed to parse root package from workflow_id: {} | error={}",
                            workflow_id, str(parse_error)
                        )
                    try:
                        # Create child workflow envelope for this codebase with RETRYING status
                        child_env = CodebaseWorkflowDbActivityEnvelope(
                            repository_name=repository_name,
                            repository_owner_name=repository_owner_name,
                            root_package=target_root_package, #type: ignore
                            codebase_workflow_id=workflow_id,
                            codebase_workflow_run_id=workflow_run_id,
                            repository_workflow_run_id=parent_workflow_run_id,
                            trace_id=trace_id,
                            status=status_to_mark.value,
                            error_report=error_report
                        )
                        
                        log.debug(
                            "Marking child workflow as RETRYING | repository={}/{} | root_package={} | workflow_run_id={}",
                            repository_name, repository_owner_name, target_root_package, workflow_run_id
                        )
                        
                        # Update status for this specific codebase
                        await self.child_db_activity.update_codebase_workflow_status(child_env)
                    except Exception as status_update_error:
                        # Log but continue - we want to propagate the original exception
                        log.error(f"Failed to update {status_to_mark.value} status: {status_update_error}")
            except Exception as outer_error:
                log.error(f"Error in activity interceptor error handling: {outer_error}")
                
            # If original exception is already an ApplicationError, re-raise it
            if isinstance(e, ApplicationError):
                raise
