"""
Utilities for fast file discovery and content search using ripgrep.

This module provides async wrappers around ripgrep subprocess calls for:
- Fast file discovery using glob patterns
- Content searching within files
- Python package root detection via main.py files

All functions use asyncio.subprocess for non-blocking I/O.
"""

from __future__ import annotations

import os
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

from aiofile import async_open


async def find_files(
    patterns: List[str], search_path: str, ignore_dirs: Optional[List[str]] = None
) -> List[str]:
    """
    Find files matching glob patterns using ripgrep.

    Args:
        patterns: List of glob patterns to match (e.g., ["*.py", "requirements*.txt"])
        search_path: Directory to search in
        ignore_dirs: Optional list of directory names to ignore

    Returns:
        List of file paths relative to search_path

    Raises:
        FileNotFoundError: If ripgrep is not installed
        RuntimeError: If ripgrep fails with non-zero exit code
    """
    if not patterns:
        return []

    # Build ripgrep command
    cmd: List[str] = ["rg", "--files", "--sort", "path"]

    # Add ignore patterns
    if ignore_dirs:
        for ignore_dir in ignore_dirs:
            cmd.extend(["-g", f"!{ignore_dir}/"])

    # Add file patterns
    for pattern in patterns:
        cmd.extend(["-g", pattern])

    try:
        # Run ripgrep subprocess
        process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=search_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_bytes: bytes
        stderr_bytes: bytes
        stdout_bytes, stderr_bytes = await process.communicate()

        if process.returncode != 0:
            # Check if it's just "no files found" (exit code 1)
            if process.returncode == 1 and not stderr_bytes:
                return []
            stderr_str: str = stderr_bytes.decode()
            raise RuntimeError(
                f"ripgrep failed with exit code {process.returncode}: {stderr_str}"
            )

        # Parse output
        if not stdout_bytes:
            return []

        stdout_str: str = stdout_bytes.decode().strip()
        files: List[str] = stdout_str.split("\n")
        return [f for f in files if f]  # Filter empty strings

    except FileNotFoundError:
        raise FileNotFoundError("ripgrep (rg) not found. Please install ripgrep.")


async def search_in_file(file_path: str, pattern: str) -> bool:
    """
    Check if file contains a specific pattern using ripgrep.

    Args:
        file_path: Path to the file to search
        pattern: String pattern to search for (treated as literal, not regex)

    Returns:
        True if pattern is found in file, False otherwise

    Raises:
        FileNotFoundError: If ripgrep is not installed or file doesn't exist
    """
    if not os.path.exists(file_path):
        return False

    # Use -F for literal string matching (not regex)
    # Use -q for quiet mode (exit on first match)
    cmd: List[str] = ["rg", "-F", "-q", pattern, file_path]

    try:
        process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
        )

        _: bytes
        stderr_bytes: bytes
        _, stderr_bytes = await process.communicate()

        # Exit code 0 = found, 1 = not found, 2+ = error
        if process.returncode == 0:
            return True
        elif process.returncode == 1:
            return False
        else:
            stderr_str: str = stderr_bytes.decode()
            raise RuntimeError(f"ripgrep search failed: {stderr_str}")

    except FileNotFoundError:
        raise FileNotFoundError("ripgrep (rg) not found. Please install ripgrep.")


async def search_absence_in_file(file_path: str, patterns: List[str]) -> bool:
    """
    Check if file does NOT contain any of the specified patterns.

    Args:
        file_path: Path to the file to search
        patterns: List of string patterns that must be absent

    Returns:
        True if NONE of the patterns are found, False if ANY pattern is found
    """
    if not patterns:
        return True  # No patterns to check = absence condition satisfied

    # Check each pattern - if any is found, return False
    for pattern in patterns:
        pattern_found: bool = await search_in_file(file_path, pattern)
        if pattern_found:
            return False

    return True  # None of the patterns were found


async def find_files_with_content(
    content_pattern: str,
    file_glob: str,
    search_path: str,
    ignore_dirs: Optional[List[str]] = None,
) -> List[str]:
    """
    Find files matching glob pattern that contain specific content using ripgrep.

    Uses ripgrep to search for content in files matching a glob pattern.
    This is more efficient than iterating through files individually.

    Args:
        content_pattern: Literal string pattern to search for in file contents
        file_glob: Glob pattern to match files (e.g., "package.json", "*.ts")
        search_path: Directory to search in
        ignore_dirs: Optional list of directory names to ignore

    Returns:
        List of file paths (relative to search_path) that match both:
        - The glob pattern AND
        - Contain the content pattern

    Raises:
        FileNotFoundError: If ripgrep is not installed
        RuntimeError: If ripgrep fails with non-zero exit code

    Example:
        # Find all package.json files containing "typescript"
        files = await find_files_with_content("typescript", "package.json", "/repo")
    """
    # Build ripgrep command
    # -F: Literal string search (not regex)
    # -l: Files-with-matches (return only filenames, not matching lines)
    # -g: Glob pattern to filter files
    cmd: List[str] = ["rg", "-F", "-l", content_pattern, "-g", file_glob]

    # Add ignore patterns if provided
    if ignore_dirs:
        for ignore_dir in ignore_dirs:
            cmd.extend(["-g", f"!{ignore_dir}/"])

    try:
        # Run ripgrep subprocess
        process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=search_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_bytes: bytes
        stderr_bytes: bytes
        stdout_bytes, stderr_bytes = await process.communicate()

        # Exit codes: 0 = found, 1 = not found, 2+ = error
        if process.returncode == 0:
            # Pattern found in files
            if not stdout_bytes:
                return []
            stdout_str: str = stdout_bytes.decode().strip()
            files: List[str] = stdout_str.split("\n")
            return [f for f in files if f]  # Filter empty strings
        elif process.returncode == 1:
            # No files found matching both glob and content
            return []
        else:
            # Error occurred
            stderr_str: str = stderr_bytes.decode()
            raise RuntimeError(
                f"ripgrep failed with exit code {process.returncode}: {stderr_str}"
            )

    except FileNotFoundError:
        raise FileNotFoundError("ripgrep (rg) not found. Please install ripgrep.")


async def parse_package_json_dependencies(package_json_path: str) -> bool:
    """
    Parse package.json and check if TypeScript is in dependency sections.

    Checks for "typescript" package in:
    - dependencies
    - devDependencies
    - peerDependencies
    - optionalDependencies

    This provides precise detection avoiding false positives from keywords,
    descriptions, or other non-dependency fields.

    Args:
        package_json_path: Absolute path to package.json file

    Returns:
        True if "typescript" found in any dependency section, False otherwise

    Raises:
        FileNotFoundError: If package.json doesn't exist
        json.JSONDecodeError: If package.json is invalid JSON
    """
    package_json_file = Path(package_json_path)
    if not package_json_file.exists():
        raise FileNotFoundError(f"package.json not found: {package_json_path}")

    # Read package.json asynchronously
    async with async_open(package_json_path, "r") as f:
        content: str = await f.read()

    # Parse JSON
    try:
        package_data: Dict = json.loads(content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {package_json_path}: {e.msg}", e.doc, e.pos
        )

    # Check all dependency sections for "typescript"
    dependency_sections = [
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
    ]

    for section in dependency_sections:
        if section in package_data:
            deps: Dict = package_data[section]
            if isinstance(deps, dict) and "typescript" in deps:
                return True

    return False


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


async def check_ripgrep_available() -> bool:
    """
    Check if ripgrep is available on the system.

    Returns:
        True if ripgrep is available, False otherwise
    """
    try:
        process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
            "rg",
            "--version",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.communicate()
        return process.returncode == 0
    except FileNotFoundError:
        return False
