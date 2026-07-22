"""Backend permission contracts for call-expression discovery.

These tests exercise the real resolved LocalBackend ruleset. They intentionally
do not run an agent model.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_ai_backends.backends.local import LocalBackend
import pytest

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    CALL_EXPRESSION_DISCOVERY_RULESET,
    READONLY_CONSOLE_RULESET,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_resolver import (
    resolve_agent_backend,
)

_MATCH_MARKER = "UNIQUE_CALL_EXPRESSION_DISCOVERY_MARKER_HTTPX_POST"
_MATCH_LINE = f'await client.post("/orders")  # {_MATCH_MARKER}'

_PRODUCTION_MAIN = Path("src/main.py")
_TEST_MAIN = Path("tests/test_main.py")
_TEST_DATA_COPY = Path("tests/test_data/copied.py")
_SPEC_FILE = Path("src/example.spec.ts")
_JS_EXACT_TEST = Path("test.ts")
_JS_PREFIX_TEST = Path("src/test_foo.ts")
_JS_SUFFIX_TEST = Path("src/foo_test.ts")
_DENIED_RELATIVE_PATHS = (
    _TEST_MAIN,
    _TEST_DATA_COPY,
    _SPEC_FILE,
    _JS_EXACT_TEST,
    _JS_PREFIX_TEST,
    _JS_SUFFIX_TEST,
)


def _build_metadata(codebase_path: Path) -> CodebaseMetadata:
    path = str(codebase_path)
    return CodebaseMetadata(
        codebase_name="apps/api",
        codebase_path=path,
        codebase_programming_language="python",
        codebase_package_manager="uv",
        codebase_package_manager_provenance="local",
        codebase_workspace_root=".",
        codebase_workspace_root_path=path,
    )


@pytest.fixture
def discovery_repo(tmp_path: Path) -> Path:
    """Build a codebase with identical marker text in production and test paths."""
    codebase_root = tmp_path / "apps" / "api"
    (codebase_root / "src").mkdir(parents=True)
    (codebase_root / "tests" / "test_data").mkdir(parents=True)

    (codebase_root / _PRODUCTION_MAIN).write_text(f"{_MATCH_LINE}\n", encoding="utf-8")
    (codebase_root / _TEST_MAIN).write_text(f"{_MATCH_LINE}\n", encoding="utf-8")
    (codebase_root / _TEST_DATA_COPY).write_text(f"{_MATCH_LINE}\n", encoding="utf-8")
    (codebase_root / _SPEC_FILE).write_text(f"{_MATCH_LINE}\n", encoding="utf-8")
    (codebase_root / _JS_EXACT_TEST).write_text(f"{_MATCH_LINE}\n", encoding="utf-8")
    (codebase_root / _JS_PREFIX_TEST).write_text(f"{_MATCH_LINE}\n", encoding="utf-8")
    (codebase_root / _JS_SUFFIX_TEST).write_text(f"{_MATCH_LINE}\n", encoding="utf-8")
    return codebase_root


def _resolve_backend(agent_name: str, codebase_root: Path) -> LocalBackend:
    backend = resolve_agent_backend(
        agent_name=agent_name,
        metadata=_build_metadata(codebase_root),
        workflow_run_id="run-call-expression-discovery",
    )
    assert isinstance(backend, LocalBackend)
    return backend


def _path_entry(value: object) -> str:
    if isinstance(value, dict):
        path = value.get("path", "")
    else:
        path = getattr(value, "path", value)
    return str(path).replace("\\", "/")


def _ends_with_relative(path: str, relative: Path) -> bool:
    normalized = path.replace("\\", "/").rstrip("/")
    suffix = relative.as_posix()
    return normalized == suffix or normalized.endswith(f"/{suffix}")


def _entry_names(entries: list[object]) -> set[str]:
    names: set[str] = set()
    for entry in entries:
        if isinstance(entry, dict):
            name = entry.get("name")
            if name is None:
                name = Path(_path_entry(entry)).name
        else:
            name = getattr(entry, "name", None)
            if name is None:
                name = Path(_path_entry(entry)).name
        names.add(str(name))
    return names


def test_call_expression_discoverer_backend_uses_specialized_readonly_ruleset(
    discovery_repo: Path,
) -> None:
    backend = _resolve_backend("call_expression_discoverer", discovery_repo)

    assert backend.execute_enabled is False
    assert backend.permissions == CALL_EXPRESSION_DISCOVERY_RULESET
    assert backend.root_dir == discovery_repo.resolve()


def test_call_expression_discoverer_grep_returns_only_production_matches(
    discovery_repo: Path,
) -> None:
    backend = _resolve_backend("call_expression_discoverer", discovery_repo)

    matches = backend.grep_raw(_MATCH_MARKER)
    assert isinstance(matches, list)
    assert matches, "expected at least one production grep match"

    match_paths = [_path_entry(match) for match in matches]
    assert len(match_paths) == 1
    assert _ends_with_relative(match_paths[0], _PRODUCTION_MAIN)
    assert all(
        not _ends_with_relative(path, denied)
        for path in match_paths
        for denied in _DENIED_RELATIVE_PATHS
    )

    match_lines = [
        str(match.get("line", "") if isinstance(match, dict) else getattr(match, "line", match))
        for match in matches
    ]
    assert all(_MATCH_MARKER in line for line in match_lines)


def test_call_expression_discoverer_glob_excludes_test_and_spec_files(
    discovery_repo: Path,
) -> None:
    backend = _resolve_backend("call_expression_discoverer", discovery_repo)

    entries = backend.glob_info("**/*")
    paths = [_path_entry(entry) for entry in entries]

    assert any(_ends_with_relative(path, _PRODUCTION_MAIN) for path in paths)
    assert all(
        not _ends_with_relative(path, denied) for path in paths for denied in _DENIED_RELATIVE_PATHS
    )
    assert all("/tests/" not in path.replace("\\", "/") for path in paths)
    assert all(not path.replace("\\", "/").endswith(".spec.ts") for path in paths)


def test_call_expression_discoverer_ls_hides_denied_test_directories(
    discovery_repo: Path,
) -> None:
    backend = _resolve_backend("call_expression_discoverer", discovery_repo)

    root_entries = backend.ls_info(".")
    names = _entry_names(root_entries)

    assert "src" in names
    assert "tests" not in names
    assert "test" not in names
    assert "__tests__" not in names
    assert "test_data" not in names


def test_call_expression_discoverer_read_allows_production_and_denies_tests(
    discovery_repo: Path,
) -> None:
    backend = _resolve_backend("call_expression_discoverer", discovery_repo)

    production = backend.read(_PRODUCTION_MAIN.as_posix())
    assert isinstance(production, str)
    assert "Permission denied" not in production
    assert _MATCH_MARKER in production

    for denied in _DENIED_RELATIVE_PATHS:
        result = backend.read(denied.as_posix())
        assert isinstance(result, str)
        assert result.startswith("Error: Permission denied")
        assert _MATCH_MARKER not in result
        assert _MATCH_LINE not in result


def test_dependency_guide_backend_remains_unfiltered_readonly(
    discovery_repo: Path,
) -> None:
    backend = _resolve_backend("dependency_guide", discovery_repo)

    assert backend.execute_enabled is False
    assert backend.permissions == READONLY_CONSOLE_RULESET

    matches = backend.grep_raw(_MATCH_MARKER)
    assert isinstance(matches, list)
    match_paths = [_path_entry(match) for match in matches]
    assert any(_ends_with_relative(path, _PRODUCTION_MAIN) for path in match_paths)
    assert any(_ends_with_relative(path, _TEST_MAIN) for path in match_paths)
    assert any(_ends_with_relative(path, _TEST_DATA_COPY) for path in match_paths)
    assert any(_ends_with_relative(path, _SPEC_FILE) for path in match_paths)
    assert any(_ends_with_relative(path, _JS_EXACT_TEST) for path in match_paths)
    assert any(_ends_with_relative(path, _JS_PREFIX_TEST) for path in match_paths)
    assert any(_ends_with_relative(path, _JS_SUFFIX_TEST) for path in match_paths)

    test_contents = backend.read(_TEST_MAIN.as_posix())
    assert isinstance(test_contents, str)
    assert "Permission denied" not in test_contents
    assert _MATCH_MARKER in test_contents
