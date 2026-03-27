"""Python-specific ripgrep utilities."""

from __future__ import annotations

import os
from typing import List

from src.code_confluence_flow_bridge.parser.package_manager.shared.ripgrep import (
    find_files,
)


async def find_python_mains(search_path: str, codebase_subdir: str = ".") -> List[str]:
    """
    Find all main.py files for Python root package detection.

    Args:
        search_path: Repository root path
        codebase_subdir: Subdirectory within repo to search (default: "." for repo root)

    Returns:
        List of directory paths containing main.py files, relative to codebase_subdir
    """
    # Build search path
    full_search_path: str
    prefix: str
    if codebase_subdir == ".":
        full_search_path = search_path
        prefix = ""
    else:
        full_search_path = os.path.join(search_path, codebase_subdir)
        prefix = codebase_subdir + "/"

    # Find all main.py files
    main_files: List[str] = await find_files(["main.py"], full_search_path)

    # Extract package directories
    packages: List[str] = []
    for main_file in main_files:
        # Convert to path relative to codebase_subdir
        rel_path: str
        if prefix and main_file.startswith(prefix):
            rel_path = main_file[len(prefix) :]
        else:
            rel_path = main_file

        # Determine package directory
        if rel_path == "main.py":
            # main.py at codebase root
            packages.append(".")
        else:
            # main.py in subdirectory
            package_dir: str = os.path.dirname(rel_path)
            if package_dir and package_dir not in packages:
                packages.append(package_dir)

    # Sort for consistent output
    return sorted(packages)
