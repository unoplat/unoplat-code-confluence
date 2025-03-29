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