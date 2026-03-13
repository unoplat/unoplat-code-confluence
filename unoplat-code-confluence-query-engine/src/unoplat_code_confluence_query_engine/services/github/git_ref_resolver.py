"""Resolve repository default branch and head commit SHA via GitHub API."""

from __future__ import annotations

from ghapi.core import GhApi

from unoplat_code_confluence_query_engine.models.output.git_ref_info import GitRefInfo


def resolve_repository_git_ref(api: GhApi, owner: str, repo: str) -> GitRefInfo:
    """Resolve default branch and head commit SHA via GitHub API.

    Uses ghapi's high-level methods:
    - ``api.repos.get()`` to retrieve repository info (including default_branch)
    - ``api.git.get_ref()`` to retrieve the HEAD commit SHA of the default branch

    Args:
        api: Authenticated GhApi instance.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        GitRefInfo with default_branch and head_commit_sha.

    Raises:
        ValueError: If required fields are missing from GitHub API responses.
    """
    repo_info = api.repos.get(owner=owner, repo=repo)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
    default_branch: str | None = getattr(repo_info, "default_branch", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    if not isinstance(default_branch, str) or not default_branch:
        raise ValueError("GitHub API response missing 'default_branch' field")

    ref_info = api.git.get_ref(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
        owner=owner,
        repo=repo,
        ref=f"heads/{default_branch}",
    )
    ref_object: object = getattr(ref_info, "object", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    if ref_object is None:
        raise ValueError("GitHub API response missing 'object' in git.get_ref response")

    head_sha: str | None = getattr(ref_object, "sha", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    if not isinstance(head_sha, str) or not head_sha:
        raise ValueError("GitHub API response missing 'sha' in git.get_ref.object")

    return GitRefInfo(default_branch=default_branch, head_commit_sha=head_sha)
