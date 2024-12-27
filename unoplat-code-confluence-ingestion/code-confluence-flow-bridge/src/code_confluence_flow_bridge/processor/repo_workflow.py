from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, Any, Optional

from temporalio import workflow, activity


with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.processor.git_activity.confluence_git_activity import GitActivity

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.configuration.settings import RepositorySettings
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository


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
        
        # Execute git activity with retry policy
        result: UnoplatGitRepository = await workflow.execute_activity(
            activity=GitActivity.process_git_activity,
            args=(repository_settings, github_token),
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        return result
                
