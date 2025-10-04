"""Common git helpers for ripgrep-based detectors."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from git import Repo


def _default_base_dir() -> Path:
    """Return the canonical base directory for detector-managed clones."""
    return Path.home() / ".unoplat" / "repositories"


def compute_local_repo_path(git_url: str, base_dir: Optional[Path] = None) -> Path:
    """Resolve the local path for a repository given its remote URL."""
    base_dir = base_dir or _default_base_dir()

    if git_url.startswith("git@"):
        repo_path = git_url.split("github.com:")[-1]
    else:
        repo_path = git_url.split("github.com/")[-1]

    repo_path = repo_path.replace(".git", "")
    repo_name = repo_path.split("/")[-1]
    return Path(os.path.expanduser(str(base_dir))) / repo_name


def clone_repo_if_missing(
    git_url: str,
    github_token: str,
    *,
    depth: int = 1,
    base_dir: Optional[Path] = None,
) -> Path:
    """Clone the repository if it does not exist locally."""
    local_repo_path = compute_local_repo_path(git_url, base_dir)
    local_repo_path.parent.mkdir(parents=True, exist_ok=True)

    if not local_repo_path.exists():
        clone_url = (
            git_url.replace("https://", f"https://{github_token}@")
            if git_url.startswith("https://")
            else git_url
        )
        Repo.clone_from(clone_url, local_repo_path, depth=depth)

    return local_repo_path
