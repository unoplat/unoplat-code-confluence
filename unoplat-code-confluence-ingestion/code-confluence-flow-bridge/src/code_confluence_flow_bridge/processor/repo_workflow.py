from temporalio import workflow
from temporalio.client import WorkflowFailureError
from temporalio.exceptions import ActivityError, ApplicationError
from temporalio.workflow import ChildWorkflowHandle, ParentClosePolicy

with workflow.unsafe.imports_passed_through():
    import asyncio
    from datetime import timedelta

    from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
        CodebaseChildWorkflowEnvelope,
        ConfluenceGitGraphEnvelope,
        GitActivityEnvelope,
        RepoWorkflowRunEnvelope,
    )
    from src.code_confluence_flow_bridge.processor.activity_retries_config import (
        ActivityRetriesConfig,
    )
    from src.code_confluence_flow_bridge.processor.codebase_child_workflow import (
        CodebaseChildWorkflow,
    )
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import (
        GitActivity,
    )
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_graph import (
        ConfluenceGitGraph,
    )


with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
        UnoplatGitRepository,
    )
    from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import (
        ParentChildCloneMetadata,
    )


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
        # Get workflow run ID for child workflow envelope
        info: workflow.Info = workflow.info()
        workflow_run_id: str = info.run_id

        try:
            workflow.logger.info(
                "Starting repository workflow for %s", repo_request.repository_git_url
            )

            workflow.logger.info("Executing git activity to process repository")
            # Create GitActivityEnvelope
            git_activity_envelope = GitActivityEnvelope(
                repo_request=repo_request, github_token=github_token, trace_id=trace_id
            )
            git_repo_metadata: UnoplatGitRepository = await workflow.execute_activity(
                activity=GitActivity.process_git_activity,
                args=[git_activity_envelope],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=ActivityRetriesConfig.DEFAULT,
            )

            # 2. Then insert the git repo into relational tables
            workflow.logger.info(
                "Inserting git repository metadata into relational tables"
            )
            # Create ConfluenceGitGraphEnvelope
            git_graph_envelope = ConfluenceGitGraphEnvelope(
                git_repo=git_repo_metadata, trace_id=trace_id
            )
            parent_child_clone_metadata: ParentChildCloneMetadata = (
                await workflow.execute_activity(
                    activity=ConfluenceGitGraph.insert_git_repo_into_graph_db,
                    args=[git_graph_envelope],
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=ActivityRetriesConfig.DEFAULT,
                )
            )

            # 3. Then spawns child workflows for each codebase
            workflow.logger.info(
                "Starting %s child workflows for codebases",
                len(git_repo_metadata.codebases),
            )
            # track child handles so we can await them later
            child_handles: list[ChildWorkflowHandle] = []

            for codebase_qualified_name, unoplat_codebase in zip(
                parent_child_clone_metadata.codebase_qualified_names,
                git_repo_metadata.codebases,
            ):
                workflow.logger.info(
                    "Starting child workflow for codebase: %s", codebase_qualified_name
                )
                workflow.logger.debug(
                    "Child workflow args: repository_qualified_name=%s, codebase_qualified_name=%s, root_packages=%s, codebase_path=%s, package_manager_metadata=%s",
                    parent_child_clone_metadata.repository_qualified_name,
                    codebase_qualified_name,
                    unoplat_codebase.root_packages,
                    unoplat_codebase.codebase_path,
                    unoplat_codebase.package_manager_metadata,
                )
                # Generate a unique workflow ID for the child workflow
                child_workflow_id = f"codebase-child-workflow_{codebase_qualified_name}"
                try:
                    # Create CodebaseChildWorkflowEnvelope
                    child_workflow_envelope = CodebaseChildWorkflowEnvelope(
                        repository_qualified_name=parent_child_clone_metadata.repository_qualified_name,
                        codebase_qualified_name=codebase_qualified_name,
                        root_packages=unoplat_codebase.root_packages,
                        codebase_path=unoplat_codebase.codebase_path,
                        codebase_folder=unoplat_codebase.codebase_folder,
                        package_manager_metadata=unoplat_codebase.package_manager_metadata,
                        trace_id=trace_id,
                        parent_workflow_run_id=workflow_run_id,
                    )
                    child_handle: ChildWorkflowHandle = (
                        await workflow.start_child_workflow(
                            CodebaseChildWorkflow.run,
                            args=[child_workflow_envelope],
                            id=child_workflow_id,
                            # use default TERMINATE policy (omit or set explicitly)
                            parent_close_policy=ParentClosePolicy.TERMINATE,
                        )
                    )
                    child_handles.append(child_handle)
                except WorkflowFailureError as wf:
                    inner: BaseException = (
                        wf.cause
                    )  # e.g. an ActivityError or ChildWorkflowError
                    workflow.logger.error(
                        "Child workflow failed | failed_entity=%s | error_message=%s | stack_trace=%s",
                        child_workflow_id,
                        str(inner),
                        inner.__traceback__,
                    )

            # Wait for all children concurrently and collect results

            results = await asyncio.gather(
                *child_handles,  # ← each handle awaits its own completion
                return_exceptions=True,  # collect failures instead of raising
            )

            any_failed = any(isinstance(r, BaseException) for r in results)
            if any_failed:
                workflow.logger.warning(
                    "One or more codebase child workflows failed for repository %s",
                    repo_request.repository_git_url,
                )

            workflow.logger.info(
                "Repository workflow completed successfully for %s",
                repo_request.repository_git_url,
            )
            return git_repo_metadata
        except ActivityError as e:
            if e.cause is not None and isinstance(e.cause, ApplicationError):
                error_type: ApplicationError = e.cause
                workflow.logger.error(
                    "Parent workflow failed | error_type=%s | error_message=%s | details=%s | non_retryable=%s | stack_trace=%s",
                    error_type.type,
                    str(error_type),
                    error_type.details,
                    error_type.non_retryable,
                    error_type.__traceback__,
                )
                raise e
            else:
                workflow.logger.error(
                    "Parent workflow failed | error_message=%s | stack_trace=%s",
                    str(e),
                    e.__traceback__,
                )
            raise
