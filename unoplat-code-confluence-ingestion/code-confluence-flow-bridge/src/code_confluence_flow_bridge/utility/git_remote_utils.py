"""Utility functions for parsing Git remote URLs and extracting repository metadata."""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse


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


