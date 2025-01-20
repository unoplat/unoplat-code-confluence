from datetime import timedelta

from temporalio import workflow
from temporalio.workflow import ParentClosePolicy

from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.processor.codebase_child_workflow import CodebaseChildWorkflow
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import ConfluenceGitGraph

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
    from src.code_confluence_flow_bridge.models.configuration.settings import RepositorySettings


@workflow.defn(name="repo-activity-workflow")
class RepoWorkflow:
    """
    Workflow that orchestrates repository processing activities
    """
    
        
    @workflow.run
    async def run(self, repository_settings: RepositorySettings, github_token: str) -> UnoplatGitRepository:
        """
        Execute the repository activity workflow
        
        Args:
            repository_settings: Repository configuration
            app_settings: Application settings including GitHub token
            
        Returns:
            RepoActivityResult containing the processing outcome
        """
        workflow.logger.info(f"Starting repository workflow for {repository_settings.git_url}")
        
        # 1. First executes a git activity
        workflow.logger.info("Executing git activity to process repository")
        git_repo_metadata: UnoplatGitRepository = await workflow.execute_activity(
            activity=GitActivity.process_git_activity,
            args=(repository_settings, github_token),
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        # 2. Then insert the git repo into the graph db
        workflow.logger.info("Inserting git repository metadata into graph database")
        parent_child_clone_metadata: ParentChildCloneMetadata = await workflow.execute_activity(
            activity=ConfluenceGitGraph.insert_git_repo_into_graph_db,
            args=git_repo_metadata,
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        # 3. Then spawns child workflows for each codebase
        workflow.logger.info(f"Spawning {len(git_repo_metadata.codebases)} child workflows for codebases")
        for codebase_qualified_name, unoplat_codebase in zip(parent_child_clone_metadata.codebase_qualified_names, git_repo_metadata.codebases):
            workflow.logger.info(f"Starting child workflow for codebase: {codebase_qualified_name}")
            codebase_handle = await workflow.start_child_workflow(
                CodebaseChildWorkflow.run,
                args=[parent_child_clone_metadata.repository_qualified_name, codebase_qualified_name, unoplat_codebase.local_path, unoplat_codebase.package_manager_metadata],
                id=f"codebase-child-workflow-{codebase_qualified_name}",
                parent_close_policy=ParentClosePolicy.ABANDON
            )
        
        workflow.logger.info(f"Repository workflow completed successfully for {repository_settings.git_url}")
        return git_repo_metadata
                