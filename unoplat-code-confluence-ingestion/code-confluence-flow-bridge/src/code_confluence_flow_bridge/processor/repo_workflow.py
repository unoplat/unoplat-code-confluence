from temporalio import workflow
from temporalio.client import WorkflowFailureError
from temporalio.workflow import ChildWorkflowHandle, ParentClosePolicy

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
    from src.code_confluence_flow_bridge.processor.activity_retries_config import ActivityRetriesConfig
    from src.code_confluence_flow_bridge.processor.codebase_child_workflow import CodebaseChildWorkflow
    from src.code_confluence_flow_bridge.processor.db.postgres.parent_workflow_db_activity import ParentWorkflowDbActivity
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import ConfluenceGitGraph

    from datetime import timedelta


with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
    from src.code_confluence_flow_bridge.models.github.github_repo import GitHubRepoRequestConfiguration
    from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata




@workflow.defn(name="repo-activity-workflow")
class RepoWorkflow:
    """
    Workflow that orchestrates repository processing activities
    """

    @workflow.run
    async def run(self, repo_request: GitHubRepoRequestConfiguration, github_token: str, trace_id: str) -> UnoplatGitRepository:
        """
        Execute the repository activity workflow

        Args:
            repo_request: GitHub repository request configuration
            github_token: GitHub token

        Returns:
            RepoActivityResult containing the processing outcome
        """
        # Seed the ContextVar and bind a Loguru logger with trace_id
        info: workflow.Info = workflow.info()
        workflow_id = info.workflow_id
        workflow_run_id = info.run_id
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id)

        await workflow.execute_activity(
            activity=ParentWorkflowDbActivity.update_repository_workflow_status,
            args=[
                repo_request.repository_name,
                repo_request.repository_owner_name,
                workflow_id,
                workflow_run_id,
                trace_id,
                [cm.model_dump(mode="json") for cm in repo_request.repository_metadata]
            ],
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=ActivityRetriesConfig.DEFAULT,
        )

        log.info(f"Starting repository workflow for {repo_request.repository_git_url}")
        #TODO: insert into postgres regarding the workflow status with repo and owner composite key obtained by splitting the trace id 

        log.info("Executing git activity to process repository")
        git_repo_metadata: UnoplatGitRepository = await workflow.execute_activity(activity=GitActivity.process_git_activity, args=(repo_request, github_token,trace_id), start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT)

        # 2. Then insert the git repo into the graph db
        log.info("Inserting git repository metadata into graph database")
        parent_child_clone_metadata: ParentChildCloneMetadata = await workflow.execute_activity(activity=ConfluenceGitGraph.insert_git_repo_into_graph_db, args=(git_repo_metadata, trace_id), start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT)

        # 3. Then spawns child workflows for each codebase
        log.info(f"Spawning {len(git_repo_metadata.codebases)} child workflows for codebases")
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
            
            # Start the child workflow
            # type: ignore
            try:
                _: ChildWorkflowHandle = await workflow.start_child_workflow( 
                    CodebaseChildWorkflow.run, 
                    args=[
                        parent_child_clone_metadata.repository_qualified_name, 
                        codebase_qualified_name, 
                        unoplat_codebase.local_path,
                        unoplat_codebase.source_directory, 
                        unoplat_codebase.package_manager_metadata, 
                        trace_id,
                        repo_request.repository_metadata[index].root_package
                    ], 
                    id=child_workflow_id, 
                    parent_close_policy=ParentClosePolicy.ABANDON
                )
            except WorkflowFailureError as wf:
                inner: BaseException = wf.cause  # e.g. an ActivityError or ChildWorkflowError

                log.error(
                    "Child workflow failed | failed_entity={} | error_message={} | stack_trace={}",
                    child_workflow_id,
                    str(inner),
                    inner.__traceback__
                )
                

        log.info(f"Repository workflow completed successfully for {repo_request.repository_git_url}")
        return git_repo_metadata
