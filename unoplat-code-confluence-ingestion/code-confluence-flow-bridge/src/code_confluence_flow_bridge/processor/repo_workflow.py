from temporalio import workflow
from temporalio.client import WorkflowFailureError
from temporalio.workflow import ChildWorkflowHandle, ParentClosePolicy

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
    from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
        CodebaseChildWorkflowEnvelope,
        ConfluenceGitGraphEnvelope,
        GitActivityEnvelope,
        RepoWorkflowRunEnvelope,
    )
    from src.code_confluence_flow_bridge.processor.activity_retries_config import ActivityRetriesConfig
    from src.code_confluence_flow_bridge.processor.codebase_child_workflow import CodebaseChildWorkflow
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import ConfluenceGitGraph

    import asyncio
    from datetime import timedelta


with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
    from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata



@workflow.defn(name="repo-activity-workflow")
class RepoWorkflow:
    """
    Workflow that orchestrates repository processing activities
    """

    @workflow.run
    async def run(self, envelope: RepoWorkflowRunEnvelope) -> UnoplatGitRepository:
        """
        Execute the repository activity workflow

        Args:
            envelope: Envelope model containing repo_request, github_token, trace_id, and any extra fields.

        Returns:
            RepoActivityResult containing the processing outcome
        """
        
        repo_request = envelope.repo_request
        github_token = envelope.github_token
        trace_id = envelope.trace_id
        # Seed the ContextVar and bind a Loguru logger with trace_id
        info: workflow.Info = workflow.info()
        workflow_id = info.workflow_id
        workflow_run_id = info.run_id
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id)
      
        try:
            

            log.info(f"Starting repository workflow for {repo_request.repository_git_url}")
            #TODO: insert into postgres regarding the workflow status with repo and owner composite key obtained by splitting the trace id 

            log.info("Executing git activity to process repository")
            # Create GitActivityEnvelope
            git_activity_envelope = GitActivityEnvelope(
                repo_request=repo_request,
                github_token=github_token,
                trace_id=trace_id
            )
            git_repo_metadata: UnoplatGitRepository = await workflow.execute_activity(
                activity=GitActivity.process_git_activity, 
                args=[git_activity_envelope], 
                start_to_close_timeout=timedelta(minutes=10), 
                retry_policy=ActivityRetriesConfig.DEFAULT
            )

            # 2. Then insert the git repo into the graph db
            log.info("Inserting git repository metadata into graph database")
            # Create ConfluenceGitGraphEnvelope
            git_graph_envelope = ConfluenceGitGraphEnvelope(
                git_repo=git_repo_metadata,
                trace_id=trace_id
            )
            parent_child_clone_metadata: ParentChildCloneMetadata = await workflow.execute_activity(
                activity=ConfluenceGitGraph.insert_git_repo_into_graph_db, 
                args=[git_graph_envelope], 
                start_to_close_timeout=timedelta(minutes=10), 
                retry_policy=ActivityRetriesConfig.DEFAULT
            )

            # 3. Then spawns child workflows for each codebase
            log.info(f"Spawning {len(git_repo_metadata.codebases)} child workflows for codebases")
            # track child handles so we can await them later
            child_handles: list[ChildWorkflowHandle] = []

            for index, (codebase_qualified_name, unoplat_codebase) in enumerate(zip(parent_child_clone_metadata.codebase_qualified_names, git_repo_metadata.codebases)):
                log.info(f"Starting child workflow for codebase: {codebase_qualified_name}")
                log.debug(
                    "Child workflow args: repository_qualified_name='{}', codebase_qualified_name='{}', local_path='{}', source_directory='{}', package_manager_metadata={} ",
                    parent_child_clone_metadata.repository_qualified_name,
                    codebase_qualified_name,
                    unoplat_codebase.local_path,
                    unoplat_codebase.source_directory,
                    unoplat_codebase.package_manager_metadata
                )
                # Generate a unique workflow ID for the child workflow
                child_workflow_id = f"codebase-child-workflow-{codebase_qualified_name}"
                try:
                    # Create CodebaseChildWorkflowEnvelope
                    child_workflow_envelope = CodebaseChildWorkflowEnvelope(
                        repository_qualified_name=parent_child_clone_metadata.repository_qualified_name,
                        codebase_qualified_name=codebase_qualified_name,
                        local_path=unoplat_codebase.local_path,
                        source_directory=unoplat_codebase.source_directory,
                        package_manager_metadata=unoplat_codebase.package_manager_metadata,
                        trace_id=trace_id,
                        root_package=repo_request.repository_metadata[index].root_package
                    )
                    child_handle: ChildWorkflowHandle = await workflow.start_child_workflow(
                        CodebaseChildWorkflow.run,
                        args=[child_workflow_envelope],
                        id=child_workflow_id,
                        # use default TERMINATE policy (omit or set explicitly)
                        parent_close_policy=ParentClosePolicy.TERMINATE,
                    )
                    child_handles.append(child_handle)
                except WorkflowFailureError as wf:
                    inner: BaseException = wf.cause  # e.g. an ActivityError or ChildWorkflowError
                    log.error(
                        "Child workflow failed | failed_entity={} | error_message={} | stack_trace={}",
                        child_workflow_id,
                        str(inner),
                        inner.__traceback__
                    )
                    
            # Wait for all children concurrently and collect results
            
            results = await asyncio.gather(
                *child_handles,           # ← each handle awaits its own completion
                return_exceptions=True,   # collect failures instead of raising
            )

            any_failed = any(isinstance(r, BaseException) for r in results)
            if any_failed:
                log.warning("One or more codebase child workflows failed for repository {}", repo_request.repository_git_url)

            log.info(f"Repository workflow completed successfully for {repo_request.repository_git_url}")
            return git_repo_metadata
        except WorkflowFailureError as wf:
            parent_inner: BaseException = wf.cause
            log.error("Parent workflow failed | error_message={} | stack_trace={}", str(parent_inner), parent_inner.__traceback__)
            raise
