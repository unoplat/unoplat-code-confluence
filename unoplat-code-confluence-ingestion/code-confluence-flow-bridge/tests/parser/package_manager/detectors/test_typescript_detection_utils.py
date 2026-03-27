from pathlib import PurePosixPath

from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.workspace_utils import (
    expand_workspace_globs,
    segment_match,
)


def _match_workspace_glob(pattern: str, dir_path: str) -> bool:
    return segment_match(
        tuple(PurePosixPath(pattern).parts),
        0,
        tuple(PurePosixPath(dir_path).parts),
        0,
    )


def test_segment_aware_glob_matching() -> None:
    assert _match_workspace_glob("apps/*", "apps/web") is True
    assert _match_workspace_glob("apps/*", "apps/web/deep") is False
    assert _match_workspace_glob("apps/*-web", "apps/next-web") is True
    assert _match_workspace_glob("apps/*-web", "apps/web") is False
    assert _match_workspace_glob("packages/**", "packages/core") is True
    assert _match_workspace_glob("packages/**", "packages/core/utils") is True
    assert _match_workspace_glob("scripts", "scripts") is True
    assert _match_workspace_glob("scripts", "other") is False
    assert _match_workspace_glob("apps/*", "packages/foo") is False


def test_expand_workspace_globs_honors_negated_patterns_in_order() -> None:
    expanded = expand_workspace_globs(
        ["packages/**", "!packages/excluded/**", "packages/excluded/keep"],
        [
            "packages/core",
            "packages/excluded/app",
            "packages/excluded/keep",
            "packages/shared",
        ],
    )

    assert expanded == {
        "packages/core",
        "packages/excluded/keep",
        "packages/shared",
    }
