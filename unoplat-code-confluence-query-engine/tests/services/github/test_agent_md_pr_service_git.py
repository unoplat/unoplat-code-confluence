from collections.abc import Iterator
from pathlib import Path

from git import Actor, Repo
import pytest

from unoplat_code_confluence_query_engine.services.github.agent_md_pr_service import (
    _collect_changed_managed_artifacts,
)

TEST_ACTOR = Actor("Test Author", "test@example.com")


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


def test_returns_no_artifacts_when_managed_files_are_clean(
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

    changed = _collect_changed_managed_artifacts(
        root,
        ("architecture.d2", "architecture.svg"),
    )

    assert changed == []


def test_batches_staged_and_unstaged_changes_and_preserves_declared_order(
    git_repo: tuple[Path, Repo],
) -> None:
    root, repo = git_repo
    _commit_files(
        repo,
        root,
        {
            "architecture.d2": "initial d2",
            "architecture.svg": "initial svg",
        },
    )
    (root / "architecture.d2").write_text("unstaged d2", encoding="utf-8")
    (root / "architecture.svg").write_text("staged svg", encoding="utf-8")
    repo.index.add(["architecture.svg"])

    changed = _collect_changed_managed_artifacts(
        root,
        ("architecture.svg", "architecture.d2"),
    )

    assert changed == [root / "architecture.svg", root / "architecture.d2"]


def test_detects_staged_addition(
    git_repo: tuple[Path, Repo],
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"README.md": "initial"})
    (root / "architecture.d2").write_text("new diagram", encoding="utf-8")
    repo.index.add(["architecture.d2"])

    changed = _collect_changed_managed_artifacts(root, ("architecture.d2",))

    assert changed == [root / "architecture.d2"]


def test_detects_untracked_artifact_with_path_limited_check(
    git_repo: tuple[Path, Repo],
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"README.md": "initial"})
    (root / "architecture.svg").write_text("new render", encoding="utf-8")

    changed = _collect_changed_managed_artifacts(root, ("architecture.svg",))

    assert changed == [root / "architecture.svg"]


def test_detects_staged_rename_destination(
    git_repo: tuple[Path, Repo],
) -> None:
    root, repo = git_repo
    _commit_files(repo, root, {"legacy-diagram.d2": "diagram"})
    repo.index.move(["legacy-diagram.d2", "architecture.d2"])

    changed = _collect_changed_managed_artifacts(root, ("architecture.d2",))

    assert changed == [root / "architecture.d2"]


def test_maps_nested_codebase_artifacts_to_repository_relative_paths(
    git_repo: tuple[Path, Repo],
) -> None:
    repository_root, repo = git_repo
    codebase_root = repository_root / "services" / "api"
    _commit_files(repo, repository_root, {"services/api/AGENTS.md": "initial"})
    (codebase_root / "AGENTS.md").write_text("updated", encoding="utf-8")

    changed = _collect_changed_managed_artifacts(codebase_root, ("AGENTS.md",))

    assert changed == [codebase_root / "AGENTS.md"]


def test_handles_staged_and_untracked_artifacts_with_unborn_head(
    git_repo: tuple[Path, Repo],
) -> None:
    root, repo = git_repo
    (root / "architecture.d2").write_text("staged", encoding="utf-8")
    (root / "architecture.svg").write_text("untracked", encoding="utf-8")
    repo.index.add(["architecture.d2"])

    changed = _collect_changed_managed_artifacts(
        root,
        ("architecture.d2", "architecture.svg"),
    )

    assert changed == [root / "architecture.d2", root / "architecture.svg"]


def test_does_not_return_deleted_or_ignored_artifacts(
    git_repo: tuple[Path, Repo],
) -> None:
    root, repo = git_repo
    _commit_files(
        repo,
        root,
        {
            ".gitignore": "architecture.svg\n",
            "architecture.d2": "tracked",
        },
    )
    (root / "architecture.d2").unlink()
    (root / "architecture.svg").write_text("ignored", encoding="utf-8")

    changed = _collect_changed_managed_artifacts(
        root,
        ("architecture.d2", "architecture.svg"),
    )

    assert changed == []


def test_falls_back_to_all_existing_artifacts_outside_a_git_repository(
    tmp_path: Path,
) -> None:
    (tmp_path / "architecture.d2").write_text("diagram", encoding="utf-8")
    (tmp_path / "architecture.svg").write_text("render", encoding="utf-8")

    changed = _collect_changed_managed_artifacts(
        tmp_path,
        ("architecture.svg", "architecture.d2", "missing.md"),
    )

    assert changed == [tmp_path / "architecture.svg", tmp_path / "architecture.d2"]
