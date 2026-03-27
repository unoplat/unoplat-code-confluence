"""TypeScript-specific ripgrep utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from aiofile import async_open


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
