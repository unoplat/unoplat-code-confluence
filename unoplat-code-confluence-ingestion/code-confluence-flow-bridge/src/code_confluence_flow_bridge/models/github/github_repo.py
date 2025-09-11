from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguageMetadata,
)


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

class IssueStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    


class IssueTracking(BaseModel):
    issue_id: Optional[str] = Field(default=None, description="Issue ID associated with the error")
    issue_number: Optional[int] = Field(default=None, description="Issue number in the GitHub repository")
    issue_url: Optional[str] = Field(default=None, description="Issue URL associated with the error")
    issue_status: Optional[IssueStatus] = Field(default=None, description="Issue status associated with the error")
    created_at: Optional[str] = Field(default=None, description="Timestamp when the issue was created")

# Error report model for detailed error context
class ErrorReport(BaseModel):
    """
    Detailed error report capturing context of failure.
    """
    error_message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace of the error, if available")
    metadata: Optional[dict] = Field(default=None, description="Metadata associated with the error")
    
    

class JobStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    COMPLETED = "COMPLETED"
    RETRYING = "RETRYING"

class WorkflowRun(BaseModel):
    codebase_workflow_run_id: str = Field(description="Unique identifier for this specific run instance of the workflow.")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    status: JobStatus = Field(description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED.")
    completed_at: Optional[datetime] = Field(default=None, description="Timestamp when the workflow run completed")
    error_report: Optional[ErrorReport] = Field(default=None, description="Error report if the workflow run failed")
    issue_tracking: Optional[IssueTracking] = Field(
        default=None,
        description="GitHub issue tracking info for the workflow run"
    )
            
class WorkflowStatus(BaseModel):
    codebase_workflow_id: str = Field(description="Unique identifier for the workflow (remains constant across execution runs).")
    codebase_workflow_runs: List[WorkflowRun] = Field(description="Multiple run instances for this workflow.")

class CodebaseStatus(BaseModel):
    codebase_folder: str = Field(description="The folder path of the codebase.")
    workflows: List[WorkflowStatus] = Field(description="List of workflows under this codebase.")

class CodebaseStatusList(BaseModel):
    codebases: List[CodebaseStatus] = Field(description="List of codebases each with multiple workflows.")

class GitHubRepoRequestConfiguration(BaseModel):
    """Configuration for a GitHub repository, including codebase config and status."""
    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_git_url: str = Field(description="The git URL of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_metadata: List[CodebaseConfig] = Field(description="List of codebase configurations for the repository")
    is_local: bool = Field(default=False, description="Whether this is a local repository")
    local_path: Optional[str] = Field(default=None, description="Local filesystem path for local repositories")
    
class GitHubRepoResponseConfiguration(BaseModel):
    """Configuration for a GitHub repository, including codebase config and status."""
    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_metadata: List[CodebaseConfig] = Field(description="List of codebase configurations for the repository")
    
class CodebaseCurrentStatus(BaseModel):
    """Model for current status of a single codebase workflow run."""
    codebase_folder: str = Field(description="The folder path of the codebase")
    codebase_workflow_run_id: str = Field(description="The run ID of the codebase workflow")
    codebase_workflow_id: str = Field(description="The ID of the codebase workflow")
    status: JobStatus = Field(description="Status of the workflow run")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    completed_at: Optional[datetime] = Field(default=None, description="Timestamp when the workflow run completed")
    error_report: Optional[ErrorReport] = Field(default=None, description="Error report if the workflow run failed")
    issue_tracking: Optional[IssueTracking] = Field(
        default=None,
        description="GitHub issue tracking info for the workflow run"
    )

class GithubRepoStatus(BaseModel):
    """Model for current status of a repository workflow run and its associated codebase runs."""
    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_workflow_run_id: str = Field(description="The run ID of the repository workflow")
    repository_workflow_id: str = Field(description="The ID of the repository workflow")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    status: JobStatus = Field(description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED.")
    error_report: Optional[ErrorReport] = Field(default=None, description="Error report if the workflow run failed")
    issue_tracking: Optional[IssueTracking] = Field(
        default=None,
        description="GitHub issue tracking info for the repository workflow run"
    )
    completed_at: Optional[datetime] = Field(default=None, description="Timestamp when the workflow run completed")    
    codebase_status_list: Optional[CodebaseStatusList] = Field(default=None, description="Status of the repository workflows (optional, returned in GET)")


class ParentWorkflowJobResponse(BaseModel):
    """Response model for parent workflow job data API."""
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_workflow_run_id: str = Field(description="The run ID of the repository workflow")
    status: JobStatus = Field(description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING.")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    completed_at: Optional[datetime] = Field(default=None, description="Timestamp when the workflow run completed")


class ParentWorkflowJobListResponse(BaseModel):
    """Response model containing a list of parent workflow job data."""
    jobs: List[ParentWorkflowJobResponse] = Field(description="List of parent workflow jobs")
    
class IssueType(str, Enum):    
    REPOSITORY = "REPOSITORY"
    CODEBASE = "CODEBASE"
    
    
class GithubIssueSubmissionRequest(BaseModel):
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    parent_workflow_run_id: str = Field(description="The run ID of the parent workflow")
    error_type: IssueType = Field(description="Type of error")
    codebase_folder: Optional[str] = Field(default=None, description="Codebase folder path")
    codebase_workflow_run_id: Optional[str] = Field(default=None, description="The run ID of the codebase workflow")
    error_message_body: str = Field(description="Error message")


class IngestedRepositoryResponse(BaseModel):
    """Response model for ingested repository data."""
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    is_local: bool = Field(default=False, description="Whether this is a local repository")
    local_path: Optional[str] = Field(default=None, description="Local filesystem path for local repositories")


class IngestedRepositoriesListResponse(BaseModel):
    """Response model containing a list of ingested repositories."""
    repositories: List[IngestedRepositoryResponse] = Field(description="List of ingested repositories")


class RefreshRepositoryResponse(BaseModel):
    """Response after triggering repository refresh."""
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    workflow_id: str = Field(description="The ID of the started workflow")
    run_id: str = Field(description="The run ID of the started workflow")


class CodebaseMetadataResponse(BaseModel):
    """Response model for individual codebase metadata."""
    codebase_folder: str = Field(description="Path to codebase folder relative to repo root")
    programming_language_metadata: ProgrammingLanguageMetadata = Field(
        description="Language-specific metadata for this codebase"
    )


class CodebaseMetadataListResponse(BaseModel):
    """Response model containing list of codebase metadata for a repository."""
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    codebases: List[CodebaseMetadataResponse] = Field(
        description="List of codebase configurations with metadata"
    )
    