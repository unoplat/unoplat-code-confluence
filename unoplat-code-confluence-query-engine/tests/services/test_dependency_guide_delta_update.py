from __future__ import annotations

import pytest

from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
    DependencyGuideTarget,
)
from unoplat_code_confluence_query_engine.services.agents_md.validation.dependency_overview import (
    parse_dependency_overview_entries,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run import (
    dependency_guide_fetch_activity as fetch_activity_module,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.dependency_guide_completion_activity import (
    _render_dependency_overview_markdown,
)
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DependencyGuide,
    DependencyGuideEntry,
)
from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.dependency_guide_fetch_activity import (
    DependencyGuideFetchActivity,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEPENDENCY_OVERVIEW_ARTIFACT,
)


async def _fake_dependencies(names: list[str]) -> list[str]:
    return names


def test_parse_dependency_overview_entries_uses_exact_canonical_bullets() -> None:
    markdown_text = """# Dependencies Overview

- **Package management**: Use `pnpm` as the package manager for this codebase.
- **react**: Purpose: UI library.
- **react-dom**: Purpose: DOM bindings that mention react in purpose text.
- **@foo/bar**: Purpose: internal_dependency
- **multi-line**: Purpose: first line
  second line
"""

    assert parse_dependency_overview_entries(markdown_text) == {
        "react": "UI library.",
        "react-dom": "DOM bindings that mention react in purpose text.",
        "@foo/bar": "internal_dependency",
        "multi-line": "first line second line",
    }


def test_render_dependency_overview_includes_internal_dependency_and_preserves_order() -> None:
    rendered = _render_dependency_overview_markdown(
        guide=DependencyGuide(
            dependencies=[
                DependencyGuideEntry(name="zeta", purpose="Last but rendered first."),
                DependencyGuideEntry(name="@company/auth", purpose="internal_dependency"),
                DependencyGuideEntry(name="alpha", purpose="Rendered last."),
            ]
        ),
        package_manager="pnpm",
    )

    assert rendered == """# Dependencies Overview

- **Package management**: Use `pnpm` as the package manager for this codebase.
- **zeta**: Purpose: Last but rendered first.
- **@company/auth**: Purpose: internal_dependency
- **alpha**: Purpose: Rendered last.
"""


@pytest.mark.asyncio
async def test_fetch_dependency_guide_delta_no_previous_generates_all(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_fetch_codebase_dependencies(codebase_path: str) -> list[str]:
        return await _fake_dependencies(["fastapi", "pydantic"])

    monkeypatch.setattr(
        fetch_activity_module,
        "fetch_codebase_dependencies",
        fake_fetch_codebase_dependencies,
    )

    delta = await DependencyGuideFetchActivity().fetch_dependency_guide_delta(
        codebase_path=str(tmp_path),
        programming_language="python",
        package_manager="uv",
    )

    assert delta.reusable_entries == []
    assert delta.targets_to_generate == [
        DependencyGuideTarget(name="fastapi", source_packages=["fastapi"]),
        DependencyGuideTarget(name="pydantic", source_packages=["pydantic"]),
    ]
    assert delta.removed_names == []


@pytest.mark.asyncio
async def test_fetch_dependency_guide_delta_no_change_reuses_all(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_fetch_codebase_dependencies(codebase_path: str) -> list[str]:
        return await _fake_dependencies(["fastapi", "@company/auth"])

    monkeypatch.setattr(
        fetch_activity_module,
        "fetch_codebase_dependencies",
        fake_fetch_codebase_dependencies,
    )
    (tmp_path / DEPENDENCY_OVERVIEW_ARTIFACT).write_text(
        """# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **fastapi**: Purpose: Web framework.
- **@company/auth**: Purpose: internal_dependency
""",
        encoding="utf-8",
    )

    delta = await DependencyGuideFetchActivity().fetch_dependency_guide_delta(
        codebase_path=str(tmp_path),
        programming_language="python",
        package_manager="uv",
    )

    assert delta.reusable_entries == [
        {"name": "@company/auth", "purpose": "internal_dependency"},
        {"name": "fastapi", "purpose": "Web framework."},
    ]
    assert delta.targets_to_generate == []
    assert delta.removed_names == []


@pytest.mark.asyncio
async def test_fetch_dependency_guide_delta_add_only_generates_missing_target(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_fetch_codebase_dependencies(codebase_path: str) -> list[str]:
        return await _fake_dependencies(["fastapi", "pydantic"])

    monkeypatch.setattr(
        fetch_activity_module,
        "fetch_codebase_dependencies",
        fake_fetch_codebase_dependencies,
    )
    (tmp_path / DEPENDENCY_OVERVIEW_ARTIFACT).write_text(
        """# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **fastapi**: Purpose: Web framework.
""",
        encoding="utf-8",
    )

    delta = await DependencyGuideFetchActivity().fetch_dependency_guide_delta(
        codebase_path=str(tmp_path),
        programming_language="python",
        package_manager="uv",
    )

    assert delta.reusable_entries == [
        {"name": "fastapi", "purpose": "Web framework."}
    ]
    assert delta.targets_to_generate == [
        DependencyGuideTarget(name="pydantic", source_packages=["pydantic"])
    ]
    assert delta.removed_names == []


@pytest.mark.asyncio
async def test_fetch_dependency_guide_delta_delete_only_excludes_removed_entry(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_fetch_codebase_dependencies(codebase_path: str) -> list[str]:
        return await _fake_dependencies(["fastapi"])

    monkeypatch.setattr(
        fetch_activity_module,
        "fetch_codebase_dependencies",
        fake_fetch_codebase_dependencies,
    )
    (tmp_path / DEPENDENCY_OVERVIEW_ARTIFACT).write_text(
        """# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **fastapi**: Purpose: Web framework.
- **pydantic**: Purpose: Data validation.
""",
        encoding="utf-8",
    )

    delta = await DependencyGuideFetchActivity().fetch_dependency_guide_delta(
        codebase_path=str(tmp_path),
        programming_language="python",
        package_manager="uv",
    )

    assert delta.reusable_entries == [
        {"name": "fastapi", "purpose": "Web framework."}
    ]
    assert delta.targets_to_generate == []
    assert delta.removed_names == ["pydantic"]


@pytest.mark.asyncio
async def test_fetch_dependency_guide_delta_uses_normalized_ui_family_name(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_fetch_codebase_dependencies(codebase_path: str) -> list[str]:
        return await _fake_dependencies(
            ["@radix-ui/react-dialog", "@radix-ui/react-tabs"]
        )

    monkeypatch.setattr(
        fetch_activity_module,
        "fetch_codebase_dependencies",
        fake_fetch_codebase_dependencies,
    )
    (tmp_path / DEPENDENCY_OVERVIEW_ARTIFACT).write_text(
        """# Dependencies Overview

- **Package management**: Use `pnpm` as the package manager for this codebase.
- **Radix UI React Primitives**: Purpose: Accessible React primitives.
""",
        encoding="utf-8",
    )

    delta = await DependencyGuideFetchActivity().fetch_dependency_guide_delta(
        codebase_path=str(tmp_path),
        programming_language="typescript",
        package_manager="pnpm",
    )

    assert delta.reusable_entries == [
        {
            "name": "Radix UI React Primitives",
            "purpose": "Accessible React primitives.",
        }
    ]
    assert delta.targets_to_generate == []
    assert delta.removed_names == []
