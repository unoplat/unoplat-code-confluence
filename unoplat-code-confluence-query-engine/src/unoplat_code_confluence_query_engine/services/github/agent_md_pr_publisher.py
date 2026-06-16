"""Publish generated AGENTS.md artifacts to GitHub as one batched PR commit."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from ghapi.core import GhApi
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata

from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    extract_http_error_status,
)


def publish_agent_md_artifacts(
    api: GhApi,
    *,
    owner_name: str,
    repo_name: str,
    branch_name: str,
    files_to_publish: Sequence[tuple[str, str]],
    repository_workflow_run_id: str,
) -> PrMetadata:
    """Create a single-commit pull request containing all changed artifacts.

    This function is intentionally synchronous because ``ghapi`` uses urllib under
    the hood. Callers from async code should run it in a worker thread.
    """
    repo_info = api.repos.get(owner=owner_name, repo=repo_name)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
    default_branch: str | None = getattr(repo_info, "default_branch", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    if not isinstance(default_branch, str) or not default_branch:
        raise ValueError("GitHub API response missing 'default_branch' field")

    base_commit = api.repos.get_commit(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
        owner=owner_name,
        repo=repo_name,
        ref=default_branch,
    )
    head_sha = _get_required_str(base_commit, "sha", "repos.get_commit.sha")
    base_tree_sha = _extract_commit_tree_sha(base_commit)

    # ``files_to_publish`` has already been filtered from the refreshed local
    # repository working tree via ``git status``. Treat that local diff as the
    # source of truth here so PR creation does not need to scan the whole remote
    # repository tree or perform per-file remote content reads.
    changed_files = [rel_path for rel_path, _ in files_to_publish]
    if not changed_files:
        return PrMetadata(
            status="no_changes",
            branch_name=branch_name,
            message="No artifact changes detected against target branch",
        )

    pulls = api.pulls.list(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
        owner=owner_name,
        repo=repo_name,
        state="open",
        head=f"{owner_name}:{branch_name}",
        base=default_branch,
        per_page=1,
        page=1,
    )
    pulls_list = _coerce_sequence_to_list(pulls)
    if pulls_list:
        first_pull = pulls_list[0]
        existing_pr_url: str | None = getattr(first_pull, "html_url", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        existing_pr_number: int | None = getattr(first_pull, "number", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        if isinstance(existing_pr_url, str) and existing_pr_url:
            return PrMetadata(
                status="no_changes",
                pr_url=existing_pr_url,
                pr_number=existing_pr_number
                if isinstance(existing_pr_number, int)
                else None,
                branch_name=branch_name,
                message="PR already exists for this branch",
            )

    content_by_path = dict(files_to_publish)
    tree_entries = [
        {
            "path": rel_path,
            "mode": "100644",
            "type": "blob",
            "content": content_by_path[rel_path],
        }
        for rel_path in changed_files
    ]
    new_tree = api.git.create_tree(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
        owner=owner_name,
        repo=repo_name,
        base_tree=base_tree_sha,
        tree=tree_entries,
    )
    new_tree_sha = _get_required_str(new_tree, "sha", "git.create_tree.sha")
    if new_tree_sha == base_tree_sha:
        return PrMetadata(
            status="no_changes",
            branch_name=branch_name,
            message="No artifact changes detected against target branch",
        )

    new_commit = api.git.create_commit(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
        owner=owner_name,
        repo=repo_name,
        message=f"Update codebase artifacts from run {repository_workflow_run_id}",
        tree=new_tree_sha,
        parents=[head_sha],
    )
    new_commit_sha = _get_required_str(new_commit, "sha", "git.create_commit.sha")

    try:
        api.git.create_ref(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            owner=owner_name,
            repo=repo_name,
            ref=f"refs/heads/{branch_name}",
            sha=new_commit_sha,
        )
    except Exception as create_ref_error:
        if extract_http_error_status(create_ref_error) != 422:
            raise
        api.git.update_ref(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            owner=owner_name,
            repo=repo_name,
            ref=f"heads/{branch_name}",
            sha=new_commit_sha,
            force=True,
        )

    pr_title = f"Update codebase artifacts (run {repository_workflow_run_id[:8]})"
    pr_body_lines = [
        "## Summary",
        f"- Codebase artifact update for run `{repository_workflow_run_id}`",
        f"- Updated files: {len(changed_files)}",
        "",
        "## Changed Files",
        *[f"- `{path}`" for path in changed_files],
    ]
    created_pr = api.pulls.create(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
        owner=owner_name,
        repo=repo_name,
        title=pr_title,
        head=branch_name,
        base=default_branch,
        body="\n".join(pr_body_lines),
    )
    created_pr_url: str | None = getattr(created_pr, "html_url", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    if not isinstance(created_pr_url, str) or not created_pr_url:
        raise ValueError("GitHub API response missing 'html_url' in pulls.create")
    created_pr_number: int | None = getattr(created_pr, "number", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]

    return PrMetadata(
        status="modified",
        pr_url=created_pr_url,
        pr_number=created_pr_number if isinstance(created_pr_number, int) else None,
        branch_name=branch_name,
        changed_files=changed_files,
        message="Created pull request for codebase artifact changes",
    )


def _coerce_sequence_to_list(value: object) -> list[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        return []
    return list(value)


def _extract_commit_tree_sha(commit_response: object) -> str:
    commit_payload: object = getattr(commit_response, "commit", None)
    tree_payload: object = getattr(commit_payload, "tree", None)
    tree_sha: str | None = getattr(tree_payload, "sha", None)
    if not isinstance(tree_sha, str) or not tree_sha:
        raise ValueError(
            "GitHub API response missing 'commit.tree.sha' in repos.get_commit"
        )
    return tree_sha


def _get_required_str(payload: object, attribute: str, response_path: str) -> str:
    value: str | None = getattr(payload, attribute, None)
    if not isinstance(value, str) or not value:
        raise ValueError(f"GitHub API response missing '{response_path}'")
    return value
