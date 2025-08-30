"""Utilities for agent logging paths and node serialization."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Iterable, Optional, Union

import aiofiles
from loguru import logger


def _find_project_root(start: Optional[Path] = None) -> Path:
    """Locate the project root by looking for common repo markers.

    Searches upwards from `start` (or this file) for one of: pyproject.toml, uv.lock, .git.
    Falls back to two levels up from this file if no marker is found.
    """
    candidates = ["pyproject.toml", "uv.lock", ".git"]
    here = (start or Path(__file__).resolve()).parent
    for parent in [here, *here.parents]:
        if any((parent / c).exists() for c in candidates):
            return parent
    # Fallback: assume repository root is two levels above src
    return Path(__file__).resolve().parents[3]


def resolve_logs_dir(logs_dir: Union[str, Path]) -> Path:
    """Resolve a logs directory to an absolute path under the project root.

    - Absolute paths are returned as-is.
    - Relative paths are resolved against the project root directory.
    Ensures the directory exists.
    """
    logs_path = Path(logs_dir)
    if not logs_path.is_absolute():
        logs_path = _find_project_root() / logs_path
    logs_path.mkdir(parents=True, exist_ok=True)
    return logs_path


def get_logs_subdir(subdir: str) -> Path:
    """Return a logs subdirectory under the project root, ensuring it exists."""
    root = _find_project_root()
    path = root / "logs" / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_nodes_to_json(
    output_dir: Path,
    filename_prefix: str,
    nodes: Iterable[Any],
) -> str:
    """Serialize agent nodes and write to a timestamped JSON file.

    Returns the file path as a string.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{filename_prefix}_{timestamp}.json"
    # Ensure the parent directory exists even if caller passed a deeper subdir
    output_file.parent.mkdir(parents=True, exist_ok=True)

    serializable_nodes = []
    for i, node in enumerate(nodes):
        node_data = {"index": i, "node_type": type(node).__name__, "data": None}
        try:
            if hasattr(node, "model_dump_json"):
                node_json_str = node.model_dump_json(indent=2)  # type: ignore[attr-defined]
                node_data["data"] = json.loads(node_json_str)
            elif hasattr(node, "model_dump"):
                node_data["data"] = node.model_dump()  # type: ignore[attr-defined]
            else:
                node_data["data"] = str(node)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not serialize node {}: {}", i, e)
            node_data["data"] = {"error": str(e), "string_representation": str(node)}
        serializable_nodes.append(node_data)

    async with aiofiles.open(output_file, mode="w", encoding="utf-8") as f:
        await f.write(
            json.dumps(
                serializable_nodes,
                indent=2,
                ensure_ascii=False,
                default=str,
            )
        )

    logger.info("Saved {} nodes to {}", len(serializable_nodes), output_file)
    return str(output_file)
