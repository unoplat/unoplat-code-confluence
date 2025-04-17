from src.code_confluence_flow_bridge.models.configuration.settings import CodebaseConfig

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class GitHubOwner(BaseModel):
    """GitHub repository owner model."""
    
    login: str = Field(description="The username of the owner")
    id: int = Field(description="Unique identifier of the owner")
    node_id: str = Field(description="Node ID of the owner")
    avatar_url: str = Field(description="URL to the owner's avatar")
    html_url: str = Field(description="HTML URL of the owner")
    type: str = Field(description="Type of the owner (User, Organization)")
    site_admin: bool = Field(description="Whether the owner is a site admin")
    url: str = Field(description="API URL of the owner")


class GitHubLicense(BaseModel):
    """GitHub repository license model."""
    
    key: str = Field(description="License key")
    name: str = Field(description="License name")
    url: Optional[str] = Field(default=None, description="License URL")
    spdx_id: Optional[str] = Field(default=None, description="SPDX ID of the license")
    node_id: str = Field(description="Node ID of the license")


class GitHubRepo(BaseModel):
    """Model for GitHub repository data based on GitHub API response."""
    
    id: int = Field(description="Unique identifier of the repository")
    node_id: str = Field(description="Node ID of the repository")
    name: str = Field(description="The name of the repository")
    full_name: str = Field(description="Full name of the repository (owner/repo)")
    private: bool = Field(description="Whether the repository is private")
    owner: GitHubOwner = Field(description="Owner of the repository")
    html_url: str = Field(description="HTML URL of the repository")
    description: Optional[str] = Field(default=None, description="Repository description")
    fork: bool = Field(description="Whether the repository is a fork")
    url: str = Field(description="API URL of the repository")
    git_url: str = Field(description="Git URL of the repository")
    ssh_url: str = Field(description="SSH URL of the repository")
    clone_url: str = Field(description="Clone URL of the repository")
    default_branch: str = Field(description="Default branch of the repository")
    created_at: Optional[str] = Field(default=None, description="Repository creation date")
    updated_at: Optional[str] = Field(default=None, description="Repository last update date")
    pushed_at: Optional[str] = Field(default=None, description="Last push date")
    language: Optional[str] = Field(default=None, description="Primary language of the repository")
    license: Optional[GitHubLicense] = Field(default=None, description="Repository license")
    forks_count: int = Field(description="Number of forks")
    stargazers_count: int = Field(description="Number of stars")
    watchers_count: int = Field(description="Number of watchers")
    size: int = Field(description="Size of the repository in KB")
    open_issues_count: int = Field(description="Number of open issues")
    topics: Optional[List[str]] = Field(default=None, description="Repository topics")
    has_issues: bool = Field(description="Whether issues are enabled")
    has_projects: bool = Field(description="Whether projects are enabled")
    has_wiki: bool = Field(description="Whether the wiki is enabled")
    has_pages: bool = Field(description="Whether GitHub Pages is enabled")
    archived: bool = Field(description="Whether the repository is archived")
    disabled: bool = Field(description="Whether the repository is disabled")
    visibility: Optional[str] = Field(default=None, description="Repository visibility (public, private, internal)")


class GitHubRepoSummary(BaseModel):
    """Simplified model for GitHub repository data."""
    
    name: str = Field(description="The name of the repository")
    owner_url: str = Field(description="HTML URL of the repository owner")
    private: bool = Field(description="Whether the repository is private")
    git_url: str = Field(description="Git URL of the repository") 
    owner_name: str = Field(description="Login of the repository owner")
    
class PaginatedResponse(BaseModel):
    items: List[GitHubRepoSummary]
    per_page: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether there are more items to fetch")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for the next page of results")    


class CompletedStage(BaseModel):
    stageName: str = Field(description="Name of the completed stage.")
    status: str = Field(description="The status of this stage (e.g. 'Completed', 'Failed').")
    

class WorkflowStatusEnum(str, Enum):
    """Enum for workflow/job status with string value and description."""
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"

    @property
    def description(self) -> str:
        descriptions: dict["WorkflowStatusEnum", str] = {
            WorkflowStatusEnum.SUBMITTED: "Workflow has been submitted and is awaiting processing.",
            WorkflowStatusEnum.IN_PROGRESS: "Workflow is currently in progress.",
            WorkflowStatusEnum.COMPLETED: "Workflow has completed successfully.",
            WorkflowStatusEnum.ERROR: "Workflow encountered an error.",
        }
        return descriptions[self]


class WorkflowRun(BaseModel):
    workflowRunId: str = Field(description="Unique identifier for this specific run instance of the workflow.")
    status: WorkflowStatusEnum = Field(description="Overall job status.")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    currentStage: Optional[str] = Field(default=None, description="The stage currently in progress.")
    completedStages: List[CompletedStage] = Field(default_factory=list, description="List of stages that have been completed along with metadata.")
    totalStages: Optional[int] = Field(default=None, description="The total number of defined stages for the workflow.")

class WorkflowStatus(BaseModel):
    workflowId: str = Field(description="Unique identifier for the workflow (remains constant across execution runs).")
    workflowRuns: List[WorkflowRun] = Field(description="Multiple run instances for this workflow.")

class CodebaseStatus(BaseModel):
    codebaseName: str = Field(description="The name of the codebase.")
    workflows: List[WorkflowStatus] = Field(description="List of workflows under this codebase.")

class CodebaseStatusList(BaseModel):
    codebases: List[CodebaseStatus] = Field(description="List of codebases each with multiple workflows.")

class CodebaseRepoConfig(CodebaseConfig):
    status: Optional[CodebaseStatusList] = Field(default=None, description="Status of the repository workflows (optional, returned in GET)")

class GitHubRepoRequestConfiguration(BaseModel):
    """Configuration for a GitHub repository, including codebase config and status."""
    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_git_url: str = Field(description="The git URL of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_metadata: List[CodebaseConfig] = Field(description="List of codebase configurations for the repository")
    
class GitHubRepoResponseConfiguration(BaseModel):
    """Configuration for a GitHub repository, including codebase config and status."""
    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_workflow_status: Optional[WorkflowStatus] = Field(default=None, description="The status of the repository workflows")
    repository_metadata: List[CodebaseRepoConfig] = Field(description="List of codebase configurations for the repository")
    
    
    
    