"""Synchronous Git Data publication, separated from PR reconciliation.

Async callers run these operations in a thread. No operation reads the checkout,
force-updates a ref, or creates a PR before the service has persisted its SHA.
"""

from __future__ import annotations

import base64
from collections.abc import Mapping, Sequence
import re
from typing import cast

from ghapi.core import GhApi
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata

from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactCommitPublication,
    ArtifactManifest,
    ArtifactManifestEntry,
)
from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    extract_http_error_status,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_manifest import (
    ArtifactValidationError,
    CapturedArtifact,
    validate_artifact_bytes,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_paths import (
    ARTIFACT_BYTE_LIMITS,
)


class PublisherIdentityConflict(ValueError):
    """A run-owned branch or PR represents a different artifact identity."""


def validate_commit_sha(sha: str) -> str:
    """Require a full lowercase GitHub SHA-1 object identifier."""
    if re.fullmatch(r"[0-9a-f]{40}", sha) is None:
        raise ValueError("Invalid full Git object SHA")
    return sha


def publication_branch_name(run_id: str) -> str:
    """Use the complete run ID and reject invalid Git ref components."""
    if (
        not run_id
        or re.fullmatch(r"[A-Za-z0-9_-]+", run_id) is None
        or run_id.startswith("-")
    ):
        raise ValueError("Invalid workflow run ID for publication branch")
    return f"agents-md/{run_id}"


def _field(payload: object, key: str) -> object:
    if isinstance(payload, Mapping):
        return cast(Mapping[str, object], payload).get(key)
    return cast(object, getattr(payload, key, None))


def _required_str(payload: object, key: str) -> str:
    value = _field(payload, key)
    if not isinstance(value, str) or not value:
        raise ValueError("GitHub response is missing a required string field")
    return value


def _sequence(value: object) -> list[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError("GitHub response is missing a required array")
    return list(value)


def _request(
    api: GhApi,
    endpoint: str,
    *,
    owner_name: str,
    repo_name: str,
    route: dict[str, str] | None = None,
    query: dict[str, object] | None = None,
    data: dict[str, object] | None = None,
) -> object:
    # GhApi.__call__ is the public, fully specified endpoint API. Supplying the
    # timeout here bounds each urllib request, including recovery and PR reads.
    return api(
        f"/repos/{{owner}}/{{repo}}" + (f"/{endpoint}" if endpoint else ""),
        verb="POST" if data is not None else "GET",
        route={"owner": owner_name, "repo": repo_name, **(route or {})},
        query=query or {},
        data=data,
        timeout=30,
    )


def _default_commit(api: GhApi, owner: str, repository: str) -> tuple[str, str, str]:
    info = _request(api, "", owner_name=owner, repo_name=repository)
    branch = _required_str(info, "default_branch")
    ref_sha = _branch_sha(api, owner, repository, branch)
    if ref_sha is None:
        raise ValueError("Repository default branch is unavailable")
    return branch, ref_sha, _commit_tree_sha(api, owner, repository, ref_sha)


def _branch_sha(api: GhApi, owner: str, repository: str, branch: str) -> str | None:
    try:
        ref = _request(
            api,
            "git/ref/{ref}",
            owner_name=owner,
            repo_name=repository,
            route={"ref": f"heads/{branch}"},
        )
    except Exception as error:
        if extract_http_error_status(error) == 404:
            return None
        raise  # Auth, rate limits and transient failures are never absence.
    target = _field(ref, "object")
    if _field(target, "type") != "commit":
        raise PublisherIdentityConflict("Run branch does not point to a commit")
    return validate_commit_sha(_required_str(target, "sha"))


def _existing_pull(
    api: GhApi,
    owner: str,
    repository: str,
    branch: str,
    expected_number: int | None = None,
) -> object | None:
    # Include closed and merged PRs. A persisted PR number is resolved directly,
    # so a renamed/moved head cannot cause an unchecked replacement PR.
    number: object = expected_number
    if expected_number is None:
        pulls = _sequence(
            _request(
                api,
                "pulls",
                owner_name=owner,
                repo_name=repository,
                query={
                    "state": "all",
                    "head": f"{owner}:{branch}",
                    "per_page": 100,
                    "page": 1,
                },
            )
        )
        if len(pulls) > 1:
            raise PublisherIdentityConflict("Multiple PRs exist for this run branch")
        if not pulls:
            return None
        number = _field(pulls[0], "number")
    if not isinstance(number, int) or isinstance(number, bool):
        raise ValueError("GitHub response is missing a PR number")
    pull = _request(
        api,
        "pulls/{pull_number}",
        owner_name=owner,
        repo_name=repository,
        route={"pull_number": str(number)},
    )
    head = _field(pull, "head")
    if (
        _field(head, "ref") != branch
        or _required_str(_field(head, "repo"), "full_name").lower()
        != f"{owner}/{repository}".lower()
    ):
        raise PublisherIdentityConflict("PR head is not owned by this repository run")
    return pull


def _pull_sha(pull: object) -> str:
    return validate_commit_sha(_required_str(_field(pull, "head"), "sha"))


def _commit_tree_sha(api: GhApi, owner: str, repository: str, sha: str) -> str:
    validate_commit_sha(sha)
    commit = _request(
        api,
        "git/commits/{commit_sha}",
        owner_name=owner,
        repo_name=repository,
        route={"commit_sha": sha},
    )
    if validate_commit_sha(_required_str(commit, "sha")) != sha:
        raise ValueError("GitHub returned a different commit identity")
    return validate_commit_sha(_required_str(_field(commit, "tree"), "sha"))


def _read_remote_tree_artifact(
    api: GhApi,
    owner: str,
    repository: str,
    tree_sha: str,
    entry: ArtifactManifestEntry,
    trees: dict[str, list[object]],
) -> bytes | None:
    parts = entry.path.split("/")
    for index, part in enumerate(parts):
        if tree_sha not in trees:
            tree = _request(
                api,
                "git/trees/{tree_sha}",
                owner_name=owner,
                repo_name=repository,
                route={"tree_sha": tree_sha},
            )
            if _field(tree, "truncated") is not False:
                raise ValueError("GitHub tree listing is incomplete")
            if validate_commit_sha(_required_str(tree, "sha")) != tree_sha:
                raise ValueError("GitHub returned a different tree identity")
            trees[tree_sha] = _sequence(_field(tree, "tree"))
        matches = [item for item in trees[tree_sha] if _field(item, "path") == part]
        if not matches:
            return None
        if len(matches) != 1:
            raise ValueError("GitHub tree contains ambiguous paths")
        item = matches[0]
        object_sha = validate_commit_sha(_required_str(item, "sha"))
        if index < len(parts) - 1:
            if _field(item, "type") != "tree" or _field(item, "mode") != "040000":
                return None
            tree_sha = object_sha
            continue
        if _field(item, "type") != "blob" or _field(item, "mode") not in {
            "100644",
            "100755",
        }:
            return None
        if _field(item, "size") != entry.byte_length:
            raise ArtifactValidationError(
                "Remote artifact size does not match manifest"
            )
        blob = _request(
            api,
            "git/blobs/{file_sha}",
            owner_name=owner,
            repo_name=repository,
            route={"file_sha": object_sha},
        )
        if validate_commit_sha(_required_str(blob, "sha")) != object_sha:
            raise ValueError("GitHub returned a different blob identity")
        if (
            _field(blob, "encoding") != "base64"
            or _field(blob, "size") != entry.byte_length
        ):
            raise ArtifactValidationError("Remote artifact encoding or size is invalid")
        encoded = _field(blob, "content")
        # GitHub wraps base64 with newlines. Bound before stripping whitespace.
        encoded_limit = ((ARTIFACT_BYTE_LIMITS[entry.kind] + 2) // 3) * 4
        if not isinstance(encoded, str) or len(encoded) > encoded_limit * 2 + 2:
            raise ArtifactValidationError("Remote artifact exceeds its byte limit")
        content = base64.b64decode("".join(encoded.split()), validate=True)
        validate_artifact_bytes(entry, content)
        return content
    return None


def verify_remote_manifest(
    api: GhApi,
    *,
    owner_name: str,
    repo_name: str,
    commit_sha: str,
    manifest: ArtifactManifest,
) -> bool:
    """Prove every frozen size/digest at one commit, never at a mutable ref."""
    if not manifest.root:
        return False
    tree_sha = _commit_tree_sha(api, owner_name, repo_name, commit_sha)
    trees: dict[str, list[object]] = {}
    for entry in manifest.root:
        try:
            content = _read_remote_tree_artifact(
                api, owner_name, repo_name, tree_sha, entry, trees
            )
        except ArtifactValidationError:
            return False
        if content is None:
            return False
    return True


def recover_artifact_commit(
    api: GhApi,
    *,
    owner_name: str,
    repo_name: str,
    branch_name: str,
    manifest: ArtifactManifest,
) -> ArtifactCommitPublication | None:
    """Try exact remote recovery BEFORE any guarded workspace retry."""
    default_branch, base_sha, _ = _default_commit(api, owner_name, repo_name)
    branch_sha = _branch_sha(api, owner_name, repo_name, branch_name)
    pull = _existing_pull(api, owner_name, repo_name, branch_name)
    pull_sha = _pull_sha(pull) if pull is not None else None
    if branch_sha is not None and pull_sha is not None and branch_sha != pull_sha:
        raise PublisherIdentityConflict(
            "Run branch and PR have conflicting commit identities"
        )
    candidate = branch_sha or pull_sha
    if candidate is not None:
        if not verify_remote_manifest(
            api,
            owner_name=owner_name,
            repo_name=repo_name,
            commit_sha=candidate,
            manifest=manifest,
        ):
            raise PublisherIdentityConflict(
                "Run branch or PR does not match the frozen manifest"
            )
        return ArtifactCommitPublication(
            commit_sha=candidate,
            status="modified",
            branch_name=branch_name,
            default_branch=default_branch,
        )
    # Recover a no_changes publication whose SHA write failed. Only a complete
    # exact-byte match at the current remote default commit is acceptable.
    if verify_remote_manifest(
        api,
        owner_name=owner_name,
        repo_name=repo_name,
        commit_sha=base_sha,
        manifest=manifest,
    ):
        return ArtifactCommitPublication(
            commit_sha=base_sha,
            status="no_changes",
            branch_name=branch_name,
            default_branch=default_branch,
        )
    return None


def _ensure_exact_ref(
    api: GhApi, owner: str, repository: str, branch: str, sha: str
) -> None:
    current = _branch_sha(api, owner, repository, branch)
    if current is not None:
        if current != sha:
            raise PublisherIdentityConflict(
                "Run branch moved; its identity cannot be replaced"
            )
        return
    try:
        _request(
            api,
            "git/refs",
            owner_name=owner,
            repo_name=repository,
            data={"ref": f"refs/heads/{branch}", "sha": sha},
        )
    except Exception as error:
        if extract_http_error_status(error) != 422:
            raise
        if _branch_sha(api, owner, repository, branch) != sha:
            raise PublisherIdentityConflict(
                "Conflicting run branch appeared during publication"
            ) from error
    if _branch_sha(api, owner, repository, branch) != sha:
        raise PublisherIdentityConflict(
            "Run branch does not retain the published commit"
        )


def publish_artifact_commit(
    api: GhApi,
    *,
    owner_name: str,
    repo_name: str,
    branch_name: str,
    captured: Sequence[CapturedArtifact],
    manifest: ArtifactManifest,
    repository_workflow_run_id: str,
) -> ArtifactCommitPublication:
    """Publish all captured files atop the CURRENT remote default tree, without a PR."""
    if [artifact.descriptor for artifact in captured] != manifest.root:
        raise ValueError("Publication bytes do not belong to the frozen inventory")
    if not manifest.root:
        raise ValueError("Empty captures have no artifact commit identity")
    default_branch, base_sha, base_tree = _default_commit(api, owner_name, repo_name)
    if (
        _branch_sha(api, owner_name, repo_name, branch_name) is not None
        or _existing_pull(
            api,
            owner_name,
            repo_name,
            branch_name,
        )
        is not None
    ):
        raise PublisherIdentityConflict(
            "Run branch or PR appeared before commit publication"
        )
    tree_entries: list[dict[str, object]] = []
    for artifact in captured:
        validate_artifact_bytes(artifact.descriptor, artifact.content)
        blob = _request(
            api,
            "git/blobs",
            owner_name=owner_name,
            repo_name=repo_name,
            data={
                "content": base64.b64encode(artifact.content).decode("ascii"),
                "encoding": "base64",
            },
        )
        tree_entries.append(
            {
                "path": artifact.descriptor.path,
                "mode": "100644",
                "type": "blob",
                "sha": validate_commit_sha(_required_str(blob, "sha")),
            }
        )
    tree = _request(
        api,
        "git/trees",
        owner_name=owner_name,
        repo_name=repo_name,
        data={"base_tree": base_tree, "tree": tree_entries},
    )
    tree_sha = validate_commit_sha(_required_str(tree, "sha"))
    if tree_sha == base_tree:
        if not verify_remote_manifest(
            api,
            owner_name=owner_name,
            repo_name=repo_name,
            commit_sha=base_sha,
            manifest=manifest,
        ):
            raise ValueError(
                "Equal-tree base commit does not verify against the manifest"
            )
        return ArtifactCommitPublication(
            commit_sha=base_sha,
            status="no_changes",
            branch_name=branch_name,
            default_branch=default_branch,
        )
    commit = _request(
        api,
        "git/commits",
        owner_name=owner_name,
        repo_name=repo_name,
        data={
            "message": f"Update codebase artifacts from run {repository_workflow_run_id}",
            "tree": tree_sha,
            "parents": [base_sha],
        },
    )
    commit_sha = validate_commit_sha(_required_str(commit, "sha"))
    if not verify_remote_manifest(
        api,
        owner_name=owner_name,
        repo_name=repo_name,
        commit_sha=commit_sha,
        manifest=manifest,
    ):
        raise ValueError("Created artifact commit does not verify against the manifest")
    _ensure_exact_ref(api, owner_name, repo_name, branch_name, commit_sha)
    return ArtifactCommitPublication(
        commit_sha=commit_sha,
        status="modified",
        branch_name=branch_name,
        default_branch=default_branch,
    )


def _pull_metadata(
    pull: object, branch: str, paths: list[str], *, created: bool
) -> PrMetadata:
    number = _field(pull, "number")
    if not isinstance(number, int) or isinstance(number, bool):
        raise ValueError("GitHub response is missing a PR number")
    # ghapi decodes JSON null as an empty AttrDict, so test for a timestamp string.
    merged_at = _field(pull, "merged_at")
    if _field(pull, "merged") is True or (isinstance(merged_at, str) and merged_at):
        message = "Artifact pull request was already merged"
    elif _field(pull, "state") == "closed":
        message = "Artifact pull request is closed; no replacement was created"
    else:
        message = (
            "Created artifact pull request"
            if created
            else "Artifact pull request already exists"
        )
    return PrMetadata(
        status="modified" if created else "no_changes",
        pr_url=_required_str(pull, "html_url"),
        pr_number=number,
        branch_name=branch,
        changed_files=paths if created else [],
        message=message,
    )


def reconcile_artifact_pr(
    api: GhApi,
    *,
    owner_name: str,
    repo_name: str,
    branch_name: str,
    commit_sha: str,
    manifest: ArtifactManifest,
    repository_workflow_run_id: str,
    expected_pr_number: int | None = None,
) -> PrMetadata:
    """Reconcile/create a PR from the SAVED commit only, never today's files."""
    validate_commit_sha(commit_sha)
    if not verify_remote_manifest(
        api,
        owner_name=owner_name,
        repo_name=repo_name,
        commit_sha=commit_sha,
        manifest=manifest,
    ):
        raise PublisherIdentityConflict(
            "Saved artifact commit does not match its manifest"
        )
    current = _branch_sha(api, owner_name, repo_name, branch_name)
    if current is not None and current != commit_sha:
        raise PublisherIdentityConflict(
            "Run branch moved away from the saved artifact commit"
        )
    paths = [entry.path for entry in manifest.root]
    pull = _existing_pull(api, owner_name, repo_name, branch_name, expected_pr_number)
    if pull is not None:
        if _pull_sha(pull) != commit_sha:
            raise PublisherIdentityConflict(
                "PR head differs from the saved artifact commit"
            )
        return _pull_metadata(pull, branch_name, paths, created=False)
    default_branch, base_sha, _ = _default_commit(api, owner_name, repo_name)
    comparison = _request(
        api,
        "compare/{basehead}",
        owner_name=owner_name,
        repo_name=repo_name,
        route={"basehead": f"{base_sha}...{commit_sha}"},
    )
    ahead_by = _field(comparison, "ahead_by")
    if not isinstance(ahead_by, int):
        raise ValueError("GitHub comparison response is missing ahead_by")
    if ahead_by == 0:
        return PrMetadata(
            status="no_changes",
            branch_name=branch_name,
            message="Saved artifact commit has no new commits against the default branch",
        )
    _ensure_exact_ref(api, owner_name, repo_name, branch_name, commit_sha)
    try:
        created = _request(
            api,
            "pulls",
            owner_name=owner_name,
            repo_name=repo_name,
            data={
                "title": f"Update codebase artifacts (run {repository_workflow_run_id[:8]})",
                "head": branch_name,
                "base": default_branch,
                "body": "\n".join(
                    [
                        "## Summary",
                        f"- Artifact update for run `{repository_workflow_run_id}`",
                        f"- Managed files: {len(paths)}",
                        "",
                        "## Files",
                        *[f"- `{path}`" for path in paths],
                    ]
                ),
            },
        )
    except Exception as error:
        if extract_http_error_status(error) != 422:
            raise
        existing = _existing_pull(api, owner_name, repo_name, branch_name)
        if existing is None:
            raise
        if _pull_sha(existing) != commit_sha:
            raise PublisherIdentityConflict(
                "PR creation raced with a conflicting identity"
            ) from error
        return _pull_metadata(existing, branch_name, paths, created=False)
    if _pull_sha(created) != commit_sha:
        raise PublisherIdentityConflict(
            "Created PR does not retain the saved commit identity"
        )
    return _pull_metadata(created, branch_name, paths, created=True)
