from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguageMetadata,
)
from unoplat_code_confluence_commons.repo_models import RepositoryProvider

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from unoplat_code_confluence_commons.repo_models import RepositoryProvider

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
    UnoplatPackageManagerMetadata,
)
from src.code_confluence_flow_bridge.models.github.github_repo import (
    ErrorReport,
    GitHubRepoRequestConfiguration,
)


class RepoWorkflowRunEnvelope(BaseModel):
    repo_request: GitHubRepoRequestConfiguration
    github_token: str
    trace_id: str
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class GitActivityEnvelope(BaseModel):
    repo_request: GitHubRepoRequestConfiguration
    github_token: str
    trace_id: str
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class ConfluenceGitGraphEnvelope(BaseModel):
    git_repo: UnoplatGitRepository
    trace_id: str
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class CodebaseChildWorkflowEnvelope(BaseModel):
    repository_qualified_name: str
    codebase_qualified_name: str
    root_packages: List[str]
    codebase_path: str
    codebase_folder: str
    package_manager_metadata: UnoplatPackageManagerMetadata
    trace_id: str
    parent_workflow_run_id: Optional[str] = None
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class ParentWorkflowDbActivityEnvelope(BaseModel):
    repository_name: str
    repository_owner_name: str
    workflow_id: Optional[str] = None
    workflow_run_id: str
    trace_id: Optional[str] = None
    repository_metadata: Optional[List[CodebaseConfig]] = None  # Using Any to avoid circular imports
    status: str  # Using string to avoid circular imports with JobStatus
    error_report: Optional[ErrorReport] = None  # Using Any to avoid circular imports
    repository_provider: RepositoryProvider = RepositoryProvider.GITHUB_OPEN
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class PackageMetadataActivityEnvelope(BaseModel):
    codebase_path: str
    programming_language_metadata: ProgrammingLanguageMetadata
    trace_id: str
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class PackageManagerMetadataIngestionEnvelope(BaseModel):
    codebase_qualified_name: str
    package_manager_metadata: UnoplatPackageManagerMetadata
    trace_id: str
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class CodebaseProcessingActivityEnvelope(BaseModel):
    root_packages: List[str]
    codebase_path: str
    repository_qualified_name: str
    codebase_qualified_name: str
    dependencies: Optional[List[str]]
    programming_language_metadata: ProgrammingLanguageMetadata
    trace_id: str
    model_config = ConfigDict(extra='allow')
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


# Envelope for codebase workflow DB activity
class CodebaseWorkflowDbActivityEnvelope(BaseModel):
    repository_name: str
    repository_owner_name: str
    codebase_folder: str
    repository_workflow_run_id: str
    codebase_workflow_id: str
    codebase_workflow_run_id: str
    trace_id: str
    status: str
    error_report: Optional[ErrorReport] = None
    model_config = ConfigDict(extra='allow')

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})
