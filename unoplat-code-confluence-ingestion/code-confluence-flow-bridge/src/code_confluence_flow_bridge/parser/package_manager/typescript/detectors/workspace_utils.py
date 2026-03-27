from __future__ import annotations

import os
from collections import defaultdict
from collections.abc import Collection, Mapping, Sequence
import fnmatch
from pathlib import PurePosixPath


def segment_match(
    pattern_parts: tuple[str, ...],
    pattern_index: int,
    dir_parts: tuple[str, ...],
    dir_index: int,
) -> bool:
    """Recursively match POSIX path segments with `**` support."""
    while pattern_index < len(pattern_parts) and dir_index < len(dir_parts):
        pattern_part = pattern_parts[pattern_index]
        if pattern_part == "**":
            if segment_match(pattern_parts, pattern_index + 1, dir_parts, dir_index):
                return True
            return segment_match(pattern_parts, pattern_index, dir_parts, dir_index + 1)
        if not fnmatch.fnmatchcase(dir_parts[dir_index], pattern_part):
            return False
        pattern_index += 1
        dir_index += 1

    while pattern_index < len(pattern_parts) and pattern_parts[pattern_index] == "**":
        pattern_index += 1

    return pattern_index == len(pattern_parts) and dir_index == len(dir_parts)


def match_workspace_pattern(pattern: str, dir_path: str) -> bool:
    """Match a workspace pattern against a repo-relative directory path."""
    return segment_match(
        PurePosixPath(pattern).parts,
        0,
        PurePosixPath(dir_path).parts,
        0,
    )


def normalize_dir_path(raw_path: str) -> str:
    """Normalize a repo-relative path to a canonical POSIX form."""
    stripped = raw_path.rstrip("/")
    if not stripped:
        return "."
    return str(PurePosixPath(stripped))


def rebase_workspace_glob(directory_path: str, glob_pattern: str) -> str:
    """Rebase a workspace glob from its declaring directory to repo-relative form."""
    is_exclusion = glob_pattern.startswith("!")
    pattern_body = glob_pattern[1:] if is_exclusion else glob_pattern
    rebased_pattern = normalize_dir_path(f"{directory_path}/{pattern_body}")
    if is_exclusion:
        return f"!{rebased_pattern}"
    return rebased_pattern


def expand_workspace_globs_with_exclusions(
    workspace_globs: Sequence[str], candidate_package_dirs: Sequence[str]
) -> tuple[set[str], set[str]]:
    """Expand workspace globs into included and excluded package-directory sets."""
    members: set[str] = set()
    excluded_dirs: set[str] = set()
    for glob_pattern in workspace_globs:
        is_exclusion = glob_pattern.startswith("!")
        pattern_body = glob_pattern[1:] if is_exclusion else glob_pattern
        normalized_pattern = normalize_dir_path(pattern_body)
        matching_dirs = {
            normalize_dir_path(dir_path)
            for dir_path in candidate_package_dirs
            if match_workspace_pattern(normalized_pattern, normalize_dir_path(dir_path))
        }
        if is_exclusion:
            members.difference_update(matching_dirs)
            excluded_dirs.update(matching_dirs)
            continue
        members.update(matching_dirs)
        excluded_dirs.difference_update(matching_dirs)
    return members, excluded_dirs


def expand_workspace_globs(
    workspace_globs: Sequence[str], candidate_package_dirs: Sequence[str]
) -> set[str]:
    """Expand workspace globs into included package directories only."""
    members, _excluded_dirs = expand_workspace_globs_with_exclusions(
        workspace_globs, candidate_package_dirs
    )
    return members


def find_nearest_workspace_owner(
    directory_path: str, aggregator_manager_map: Mapping[str, str]
) -> tuple[str, str] | None:
    """Return the deepest workspace owner that contains the directory."""
    sorted_aggregators = sorted(
        aggregator_manager_map.keys(),
        key=lambda path: len(PurePosixPath(path).parts),
        reverse=True,
    )
    for aggregator_dir in sorted_aggregators:
        if aggregator_dir == "." or directory_path.startswith(aggregator_dir + "/"):
            return aggregator_manager_map[aggregator_dir], aggregator_dir
    return None


def is_child_of_detected_codebase(
    directory_path: str, detected_standalone_dirs: Collection[str]
) -> bool:
    """Return whether the directory is nested under an emitted standalone codebase."""
    if "." in detected_standalone_dirs and directory_path != ".":
        return True
    return any(
        done_dir != "."
        and directory_path != done_dir
        and directory_path.startswith(done_dir + "/")
        for done_dir in detected_standalone_dirs
    )


def group_files_by_directory(file_paths: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Group repo-relative file paths by their parent directory."""
    dirs_to_files: dict[str, list[str]] = defaultdict(list)
    for file_path in file_paths:
        directory = os.path.dirname(file_path) or "."
        dirs_to_files[directory].append(file_path)
    return {directory: tuple(files) for directory, files in dirs_to_files.items()}
