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


<<<<<<< HEAD
def _ensure_ref(repo_path: Path, ref: str) -> None:
    """Fetch and checkout a specific commit SHA in a (possibly shallow) clone.

    GitHub supports fetching individual commits at shallow depth:
        git fetch --depth=1 origin <sha>
        git checkout <sha>

    If *ref* already matches the current HEAD, this is a no-op.
    """
    repo = Repo(repo_path)
    if repo.head.commit.hexsha == ref:
        return
    repo.git.fetch("origin", ref, depth=1)
    repo.git.checkout(ref)


=======
>>>>>>> origin/main
def clone_repo_if_missing(
    git_url: str,
    github_token: str,
    *,
    depth: int = 1,
    base_dir: Optional[Path] = None,
<<<<<<< HEAD
    ref: Optional[str] = None,
) -> Path:
    """Clone the repository if it does not exist locally.

    When *ref* is provided the working tree is moved to that exact commit,
    regardless of whether the clone was fresh or already cached.
    """
=======
) -> Path:
    """Clone the repository if it does not exist locally."""
>>>>>>> origin/main
    local_repo_path = compute_local_repo_path(git_url, base_dir)
    local_repo_path.parent.mkdir(parents=True, exist_ok=True)

    if not local_repo_path.exists():
        if git_url.startswith("https://") and github_token:
            clone_url = git_url.replace("https://", f"https://{github_token}@")
        else:
            clone_url = git_url
        Repo.clone_from(clone_url, local_repo_path, depth=depth)

<<<<<<< HEAD
    if ref is not None:
        _ensure_ref(local_repo_path, ref)

=======
>>>>>>> origin/main
    return local_repo_path
