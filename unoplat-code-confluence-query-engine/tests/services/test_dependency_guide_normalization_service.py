from __future__ import annotations

<<<<<<< HEAD
=======
# pyright: reportPrivateUsage=false
>>>>>>> origin/main
from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
    DependencyGuideTarget,
)
from unoplat_code_confluence_query_engine.services.repository.dependency_guide_normalization_service import (
    normalize_dependency_guide_targets,
)
<<<<<<< HEAD
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_dependency_guide import (
    build_dependency_guide_prompt,
=======
from unoplat_code_confluence_query_engine.services.temporal.temporal_workflows import (
    _build_dependency_guide_prompt,
>>>>>>> origin/main
)


def test_normalize_dependency_guide_targets_collapses_configured_radix_family() -> None:
    dependency_targets = normalize_dependency_guide_targets(
        dependency_names=[
            "@radix-ui/react-tabs",
            "lodash",
            "@radix-ui/react-dialog",
        ],
        programming_language="typescript",
        package_manager="pnpm",
    )

    assert dependency_targets == [
        DependencyGuideTarget(name="lodash", source_packages=["lodash"]),
        DependencyGuideTarget(
            name="Radix UI React Primitives",
            source_packages=[
                "@radix-ui/react-dialog",
                "@radix-ui/react-tabs",
            ],
            search_query="Radix UI React official documentation",
        ),
    ]


def test_normalize_dependency_guide_targets_keeps_unconfigured_family_separate() -> (
    None
):
    dependency_targets = normalize_dependency_guide_targets(
        dependency_names=[
            "@tanstack/db",
            "@tanstack/react-table",
        ],
        programming_language="typescript",
        package_manager="npm",
    )

    assert dependency_targets == [
        DependencyGuideTarget(name="@tanstack/db", source_packages=["@tanstack/db"]),
        DependencyGuideTarget(
            name="@tanstack/react-table",
            source_packages=["@tanstack/react-table"],
        ),
    ]


def test_normalize_dependency_guide_targets_collapses_configured_dnd_kit_family() -> (
    None
):
    dependency_targets = normalize_dependency_guide_targets(
        dependency_names=[
            "@dnd-kit/modifiers",
            "@dnd-kit/core",
            "@dnd-kit/sortable",
        ],
        programming_language="typescript",
        package_manager="npm",
    )

    assert dependency_targets == [
        DependencyGuideTarget(
            name="dnd kit",
            source_packages=[
                "@dnd-kit/core",
                "@dnd-kit/modifiers",
                "@dnd-kit/sortable",
            ],
            search_query="dnd kit official documentation",
        )
    ]


def test_normalize_dependency_guide_targets_is_deterministic_for_duplicates() -> None:
    first_targets = normalize_dependency_guide_targets(
        dependency_names=[
            "@radix-ui/react-tabs",
            "clsx",
            "@radix-ui/react-dialog",
            "clsx",
        ],
        programming_language="typescript",
        package_manager="bun",
    )
    second_targets = normalize_dependency_guide_targets(
        dependency_names=[
            "clsx",
            "@radix-ui/react-dialog",
            "@radix-ui/react-tabs",
        ],
        programming_language="typescript",
        package_manager="bun",
    )

    assert first_targets == second_targets


def test_normalize_dependency_guide_targets_respects_language_scope() -> None:
    dependency_targets = normalize_dependency_guide_targets(
        dependency_names=[
            "@radix-ui/react-dialog",
            "@radix-ui/react-tabs",
        ],
        programming_language="python",
        package_manager="uv",
    )

    assert dependency_targets == [
        DependencyGuideTarget(
            name="@radix-ui/react-dialog",
            source_packages=["@radix-ui/react-dialog"],
        ),
        DependencyGuideTarget(
            name="@radix-ui/react-tabs",
            source_packages=["@radix-ui/react-tabs"],
        ),
    ]


def test_build_dependency_guide_prompt_includes_search_query_and_source_packages() -> (
    None
):
<<<<<<< HEAD
    prompt = build_dependency_guide_prompt(
=======
    prompt = _build_dependency_guide_prompt(
>>>>>>> origin/main
        dependency_target=DependencyGuideTarget(
            name="Radix UI React Primitives",
            source_packages=[
                "@radix-ui/react-dialog",
                "@radix-ui/react-popover",
            ],
            search_query="Radix UI React official documentation",
        ),
        programming_language="typescript",
    )

    assert "Document the library 'Radix UI React Primitives'" in prompt
    assert "Radix UI React official documentation" in prompt
    assert "@radix-ui/react-dialog, @radix-ui/react-popover" in prompt
