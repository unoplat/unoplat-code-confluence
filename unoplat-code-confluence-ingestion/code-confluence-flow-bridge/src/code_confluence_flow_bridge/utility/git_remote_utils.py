"""Utility functions for parsing Git remote URLs and extracting repository metadata."""

import os
import re
from typing import Optional, Tuple
from urllib.parse import urlparse

from git import Repo
from loguru import logger


def parse_remote_url(remote_url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Generic parser for git remote URLs.

    Supports common SSH and HTTPS formats, including GitHub, GitLab, Bitbucket, Azure etc.

    Examples
    --------
    >>> parse_remote_url("git@github.com:org/repo.git")
    ("github.com", "org", "repo")
    >>> parse_remote_url("https://github.com/org/repo")
    ("github.com", "org", "repo")
    >>> parse_remote_url("ssh://git@bitbucket.org/team/repo.git")
    ("bitbucket.org", "team", "repo")

    Parameters
    ----------
    remote_url: str
        The raw remote URL as returned by GitPython.

    Returns
    -------
    Tuple[Optional[str], Optional[str], Optional[str]]
        (host, organisation_or_user, repository_name) – components are ``None`` if parsing fails.
    """

    # Normalise by stripping trailing ".git" if present
    url_no_git = remote_url[:-4] if remote_url.endswith(".git") else remote_url

    # Handle SSH shorthand (git@host:org/repo)
    ssh_match = re.match(r"^(?P<user>.+?)@(?P<host>[^:]+):(?P<org>[^/]+)/(?P<repo>.+)$", url_no_git)
    if ssh_match:
        return (
            ssh_match.group("host"),
            ssh_match.group("org"),
            ssh_match.group("repo"),
        )

    # Handle git+ssh scheme (ssh://git@host/org/repo)
    if url_no_git.startswith("ssh://"):
        parsed = urlparse(url_no_git)
        path_parts = parsed.path.lstrip("/").split("/", 2)
        if len(path_parts) >= 2:
            return (parsed.hostname, path_parts[0], path_parts[1])

    # Handle https/http scheme
    if url_no_git.startswith("http://") or url_no_git.startswith("https://"):
        parsed = urlparse(url_no_git)
        path_parts = parsed.path.lstrip("/").split("/", 2)
        if len(path_parts) >= 2:
            return (parsed.hostname, path_parts[0], path_parts[1])

    # If all else fails, return Nones so caller can decide fallback behaviour
    return (None, None, None)


def extract_github_organization_from_local_repo(local_path: str, fallback_owner: str) -> str:
    """Extract GitHub organization from a local repository's remote origin.
    
    For local repositories that have a GitHub remote origin, this function
    extracts the actual organization/owner name from the remote URL.
    This ensures consistent qualified name generation between PostgreSQL 
    storage and Neo4j graph database.
    
    Parameters
    ----------
    local_path : str
        Local filesystem path to the Git repository
    fallback_owner : str
        Fallback owner name to use if remote origin is not found or parseable
        
    Returns
    -------
    str
        GitHub organization/owner name extracted from remote origin,
        or fallback_owner if extraction fails
        
    Examples
    --------
    >>> extract_github_organization_from_local_repo("/path/to/dspy", "local")
    "stanfordnlp"  # extracted from git@github.com:stanfordnlp/dspy.git
    
    >>> extract_github_organization_from_local_repo("/path/to/no-remote", "local") 
    "local"  # fallback when no remote origin exists
    """
    logger.debug("Extracting GitHub organization from local repository | local_path={}", local_path)
    
    try:
        # Verify the path exists and is a valid git repository
        if not os.path.exists(local_path):
            logger.warning("Local path does not exist | local_path={}", local_path)
            return fallback_owner
            
        # Open the local repository using GitPython
        repo = Repo(local_path)
        
        # Try to get organization/owner from remote origin if it exists
        if repo.remotes and hasattr(repo.remotes, 'origin'):
            origin_url = repo.remotes.origin.url
            logger.debug("Found remote origin | url={}", origin_url)
            
            host, org, name = parse_remote_url(origin_url)
            
            if org and name:
                logger.debug("Successfully extracted GitHub organization | org={} | repo={}", org, name)
                return org
            else:
                logger.debug("Failed to parse remote origin URL | url={}", origin_url)
        else:
            logger.debug("No remote origin found in repository | local_path={}", local_path)
            
    except Exception as e:
        logger.warning("Error extracting GitHub organization | local_path={} | error={}", local_path, str(e))
    
    # Fallback to provided owner name
    logger.debug("Using fallback owner | owner={}", fallback_owner)
    return fallback_owner