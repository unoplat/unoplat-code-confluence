import asyncio
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
import threading

from git import Actor, Repo
import pytest
from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata

from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactCommitPublication,
    ArtifactIdentityResult,
    ArtifactManifest,
    ArtifactPublicationError,
)
from unoplat_code_confluence_query_engine.services.github import agent_md_pr_service
from unoplat_code_confluence_query_engine.services.github.agent_md_pr_service import (
    AgentMdPrGithubError,
    AgentMdPrMissingArtifactError,
    _RunArtifacts,
    publish_agent_md_pr,
    reconcile_agent_md_pr_after_generation,
    save_artifact_identity_after_generation,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_manifest import (
    capture_managed_artifacts,
    manifest_from_capture,
)

TEST_ACTOR = Actor("Test Author", "test@example.com")
OWNER = "acme"
REPOSITORY = "widgets"
RUN_ID = "run-1"
BRANCH = f"agents-md/{RUN_ID}"
SAVED_SHA = "a" * 40
RAW_PROVIDER_TEXT = "raw provider response with token"


@pytest.fixture
def git_repo(tmp_path: Path) -> Iterator[tuple[Path, Repo]]:
    repo = Repo.init(tmp_path)
    try:
        yield tmp_path, repo
    finally:
        repo.close()


def _commit_files(repo: Repo, root: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    repo.index.add(list(files))
    repo.index.commit(
        "test fixture",
        author=TEST_ACTOR,
        committer=TEST_ACTOR,
    )


@dataclass
class _Recorder:
    """Durable writes and side effects seen through the service's seams."""

    lock_released: bool = False
    credential_reads: int = 0
    manifests: list[ArtifactManifest] = field(default_factory=list)
    shas: list[str] = field(default_factory=list)
    errors: list[ArtifactPublicationError] = field(default_factory=list)
    pr_writes: list[tuple[PrMetadata, str | None]] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    reconciled_shas: list[str] = field(default_factory=list)


def _state(
    names: tuple[str, ...],
    manifest: ArtifactManifest | None = None,
    sha: str | None = None,
) -> _RunArtifacts:
    return _RunArtifacts(ProviderKey.GITHUB_OPEN, names, manifest, sha, None)


def _publication(sha: str, status: str) -> ArtifactCommitPublication:
    return ArtifactCommitPublication.model_validate(
        {
            "commit_sha": sha,
            "status": status,
            "branch_name": BRANCH,
            "default_branch": "main",
        }
    )


class _ServiceSeams:
    """Database and provider replacements, keeping real capture and control flow."""

    def __init__(self, recorder: _Recorder, root: Path, state: _RunArtifacts) -> None:
        self.recorder = recorder
        self.root = root
        self.state = state

    @asynccontextmanager
    async def lock(self, *_args: object, **_kwargs: object) -> AsyncIterator[None]:
        try:
            yield None
        finally:
            self.recorder.lock_released = True

    @asynccontextmanager
    async def guard(self, *_args: object, **_kwargs: object) -> AsyncIterator[None]:
        self.recorder.calls.append("capture_guard")
        yield None

    async def read_state(self, *_args: object) -> _RunArtifacts:
        return self.state

    async def checkout_root(self, *_args: object) -> Path:
        return self.root

    async def github_client(self, *_args: object) -> object:
        self.recorder.credential_reads += 1
        return object()

    async def persist_manifest(
        self, _owner: str, _repository: str, _run_id: str, manifest: ArtifactManifest
    ) -> None:
        self.recorder.manifests.append(manifest)

    async def persist_sha(
        self,
        _owner: str,
        _repository: str,
        _run_id: str,
        _manifest: ArtifactManifest,
        sha: str,
    ) -> None:
        self.recorder.shas.append(sha)

    async def persist_pr(
        self,
        _owner: str,
        _repository: str,
        _run_id: str,
        metadata: PrMetadata,
        expected_sha: str | None,
    ) -> tuple[PrMetadata, bool]:
        self.recorder.pr_writes.append((metadata, expected_sha))
        return metadata, False

    async def persist_error(
        self,
        _owner: str,
        _repository: str,
        _run_id: str,
        error: ArtifactPublicationError,
    ) -> None:
        self.recorder.errors.append(error)

    def reconcile(
        self, *_args: object, commit_sha: str, **_kwargs: object
    ) -> PrMetadata:
        self.recorder.reconciled_shas.append(commit_sha)
        return PrMetadata(status="no_changes", branch_name=BRANCH, message="reconciled")


class _BlockingCommit:
    """A commit whose provider thread runs until the test releases it."""

    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def __call__(self, *_args: object, **_kwargs: object) -> ArtifactCommitPublication:
        self.started.set()
        self.release.wait(timeout=5)
        return _publication(SAVED_SHA, "modified")


def _raise_provider_error(*_args: object, **_kwargs: object) -> None:
    raise OSError(RAW_PROVIDER_TEXT)


def _reject_call(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("A saved identity must not be recaptured or republished")


def _no_remote_commit(*_args: object, **_kwargs: object) -> None:
    return None


def _unchanged_remote_commit(
    *_args: object, **_kwargs: object
) -> ArtifactCommitPublication:
    return _publication(SAVED_SHA, "no_changes")


def _patch_service(
    monkeypatch: pytest.MonkeyPatch,
    recorder: _Recorder,
    root: Path,
    state: _RunArtifacts,
) -> None:
    seams = _ServiceSeams(recorder, root, state)
    for name, replacement in {
        "get_async_engine": object,
        "publisher_lock": seams.lock,
        "repository_capture_guard": seams.guard,
        "_read_run_artifacts": seams.read_state,
        "_checkout_root": seams.checkout_root,
        "_github_client": seams.github_client,
        "_persist_manifest": seams.persist_manifest,
        "_persist_sha": seams.persist_sha,
        "_persist_pr_metadata": seams.persist_pr,
        "_persist_error": seams.persist_error,
        "reconcile_artifact_pr": seams.reconcile,
    }.items():
        monkeypatch.setattr(agent_md_pr_service, name, replacement)


def _save_identity(required: tuple[str, ...] = ()) -> ArtifactIdentityResult:
    return asyncio.run(
        save_artifact_identity_after_generation(
            owner_name=OWNER,
            repo_name=REPOSITORY,
            repository_workflow_run_id=RUN_ID,
            required_artifact_paths=required,
        )
    )


async def _cancel_during_commit(commit: _BlockingCommit, recorder: _Recorder) -> bool:
    """Cancel while a commit thread runs; return whether the lock outlived the cancel."""
    task = asyncio.create_task(
        save_artifact_identity_after_generation(
            owner_name=OWNER,
            repo_name=REPOSITORY,
            repository_workflow_run_id=RUN_ID,
            required_artifact_paths=(),
        )
    )
    while not commit.started.is_set():
        await asyncio.sleep(0.01)
    task.cancel()
    await asyncio.sleep(0.05)
    lock_held_during_thread = not recorder.lock_released
    commit.release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    return lock_held_during_thread


def test_inventories_clean_managed_files(
    git_repo: tuple[Path, Repo],
) -> None:
    root, repo = git_repo
    _commit_files(
        repo,
        root,
        {
            "architecture.d2": "clean d2",
            "architecture.svg": "clean svg",
        },
    )
    (root / "unrelated.txt").write_text("untracked", encoding="utf-8")

    captured = capture_managed_artifacts(root, ())

    assert [artifact.descriptor.path for artifact in captured] == [
        "architecture.d2",
        "architecture.svg",
    ]
    assert [artifact.content for artifact in captured] == [b"clean d2", b"clean svg"]


def test_cancellation_during_commit_releases_lock_without_recording_failure(
    git_repo: tuple[Path, Repo],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"architecture.d2": "d2", "architecture.svg": "svg"})
    recorder = _Recorder()
    commit = _BlockingCommit()
    _patch_service(monkeypatch, recorder, root, _state(()))
    monkeypatch.setattr(agent_md_pr_service, "recover_artifact_commit", _no_remote_commit)
    monkeypatch.setattr(agent_md_pr_service, "publish_artifact_commit", commit)

    lock_held = asyncio.run(_cancel_during_commit(commit, recorder))

    assert lock_held is True
    assert recorder.lock_released is True
    assert recorder.shas == []
    assert recorder.errors == []
    assert recorder.reconciled_shas == []


def test_missing_required_output_fails_before_manifest_freeze(
    git_repo: tuple[Path, Repo],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"architecture.d2": "d2"})
    recorder = _Recorder()
    _patch_service(monkeypatch, recorder, root, _state(("",)))

    with pytest.raises(AgentMdPrMissingArtifactError):
        _save_identity(("AGENTS.md",))

    assert recorder.manifests == []
    assert recorder.shas == []
    assert [(error.code, error.stage) for error in recorder.errors] == [
        ("required_artifact_missing", "capture")
    ]

    # A frozen inventory, empty or not, is rejected without recapture or provider work.
    frozen = manifest_from_capture(capture_managed_artifacts(root, ()))
    for name in (
        "capture_managed_artifacts",
        "revalidate_manifest",
        "recover_artifact_commit",
        "publish_artifact_commit",
    ):
        monkeypatch.setattr(agent_md_pr_service, name, _reject_call)
    for frozen_manifest in (frozen, ArtifactManifest([])):
        frozen_recorder = _Recorder()
        _patch_service(
            monkeypatch, frozen_recorder, root, _state(("",), frozen_manifest)
        )

        with pytest.raises(AgentMdPrMissingArtifactError):
            _save_identity(("AGENTS.md",))

        assert frozen_recorder.manifests == []
        assert frozen_recorder.shas == []
        assert frozen_recorder.pr_writes == []
        assert frozen_recorder.credential_reads == 0
        assert frozen_recorder.calls == []
        assert [(error.code, error.stage) for error in frozen_recorder.errors] == [
            ("required_artifact_missing", "manifest")
        ]


def test_valid_empty_inventory_records_explicit_no_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = _Recorder()
    _patch_service(monkeypatch, recorder, tmp_path, _state(()))

    result = _save_identity()

    assert result == ArtifactIdentityResult(status="no_artifacts")
    assert recorder.manifests == [ArtifactManifest([])]
    assert recorder.shas == []
    assert recorder.credential_reads == 0
    assert [(meta.status, sha) for meta, sha in recorder.pr_writes] == [
        ("no_artifacts", None)
    ]


def test_pre_sha_failure_raises_safe_error_without_saving_identity(
    git_repo: tuple[Path, Repo],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"architecture.d2": "d2", "architecture.svg": "svg"})
    recorder = _Recorder()
    _patch_service(monkeypatch, recorder, root, _state(()))
    monkeypatch.setattr(
        agent_md_pr_service, "recover_artifact_commit", _raise_provider_error
    )

    with pytest.raises(AgentMdPrGithubError) as raised:
        _save_identity()

    assert raised.value.retryable is True
    assert len(recorder.manifests) == 1
    assert recorder.shas == []
    assert recorder.reconciled_shas == []
    assert [(error.stage, error.retryable) for error in recorder.errors] == [
        ("recovery", True)
    ]
    assert RAW_PROVIDER_TEXT not in recorder.errors[0].message


def test_maps_nested_codebase_artifacts_to_repository_relative_paths(
    git_repo: tuple[Path, Repo],
) -> None:
    repository_root, repo = git_repo
    codebase_root = repository_root / "services" / "api"
    _commit_files(repo, repository_root, {"services/api/AGENTS.md": "initial"})
    (codebase_root / "AGENTS.md").write_text("updated", encoding="utf-8")

    captured = capture_managed_artifacts(repository_root, ("services/api",))

    assert [
        (artifact.descriptor.path, artifact.descriptor.codebase_name)
        for artifact in captured
    ] == [("services/api/AGENTS.md", "services/api")]
    assert captured[0].content == b"updated"


def test_unchanged_inventory_saves_verified_default_branch_sha(
    git_repo: tuple[Path, Repo],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"architecture.d2": "d2", "architecture.svg": "svg"})
    recorder = _Recorder()
    _patch_service(monkeypatch, recorder, root, _state(()))
    monkeypatch.setattr(
        agent_md_pr_service, "recover_artifact_commit", _unchanged_remote_commit
    )

    result = _save_identity(("architecture.d2", "architecture.svg"))

    assert result == ArtifactIdentityResult(status="saved", commit_sha=SAVED_SHA)
    assert [entry.path for entry in recorder.manifests[0].root] == [
        "architecture.d2",
        "architecture.svg",
    ]
    assert recorder.shas == [SAVED_SHA]
    # The required phase ends at the durable save; PR work is a separate phase.
    assert recorder.reconciled_shas == []
    assert recorder.pr_writes == []

    # A frozen inventory holding every required path proceeds to recovery as is.
    frozen_recorder = _Recorder()
    _patch_service(
        monkeypatch, frozen_recorder, root, _state((), recorder.manifests[0])
    )
    assert _save_identity(("architecture.d2", "architecture.svg")) == result
    assert frozen_recorder.manifests == []
    assert frozen_recorder.shas == [SAVED_SHA]


def test_post_sha_pr_failure_records_safe_error_and_retains_identity(
    git_repo: tuple[Path, Repo],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"architecture.d2": "d2", "architecture.svg": "svg"})
    manifest = manifest_from_capture(capture_managed_artifacts(root, ()))
    recorder = _Recorder()
    _patch_service(monkeypatch, recorder, root, _state((), manifest, SAVED_SHA))
    monkeypatch.setattr(
        agent_md_pr_service, "reconcile_artifact_pr", _raise_provider_error
    )

    with pytest.raises(AgentMdPrGithubError):
        asyncio.run(
            reconcile_agent_md_pr_after_generation(
                owner_name=OWNER,
                repo_name=REPOSITORY,
                repository_workflow_run_id=RUN_ID,
            )
        )

    assert [(error.code, error.stage) for error in recorder.errors] == [
        ("pr_creation_failed", "pr_create")
    ]
    assert RAW_PROVIDER_TEXT not in recorder.errors[0].message
    assert recorder.manifests == []
    assert recorder.shas == []
    assert recorder.pr_writes == []
    assert recorder.calls == []


def test_saved_identity_wins_on_retry_without_recapture(
    git_repo: tuple[Path, Repo],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"architecture.d2": "d2", "architecture.svg": "svg"})
    manifest = manifest_from_capture(capture_managed_artifacts(root, ()))
    # Newer checkout bytes must not influence a run whose identity is saved.
    (root / "architecture.d2").write_text("newer d2", encoding="utf-8")
    recorder = _Recorder()
    _patch_service(monkeypatch, recorder, root, _state((), manifest, SAVED_SHA))
    for name in (
        "capture_managed_artifacts",
        "revalidate_manifest",
        "recover_artifact_commit",
        "publish_artifact_commit",
    ):
        monkeypatch.setattr(agent_md_pr_service, name, _reject_call)

    # The saved inventory lacks AGENTS.md, and the saved identity still wins.
    automatic = _save_identity(("AGENTS.md",))
    assert automatic == ArtifactIdentityResult(status="saved", commit_sha=SAVED_SHA)
    assert recorder.errors == []
    assert recorder.credential_reads == 0

    metadata, _ = asyncio.run(
        publish_agent_md_pr(
            owner_name=OWNER,
            repo_name=REPOSITORY,
            repository_workflow_run_id=RUN_ID,
        )
    )

    assert metadata.message == "reconciled"
    assert recorder.reconciled_shas == [SAVED_SHA]
    assert recorder.shas == []
    assert recorder.manifests == []
    assert recorder.calls == []
