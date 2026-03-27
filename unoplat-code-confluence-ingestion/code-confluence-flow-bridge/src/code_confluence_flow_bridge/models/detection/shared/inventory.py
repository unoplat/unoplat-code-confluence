"""Shared file-inventory model for codebase detection."""

# Standard Library
from typing import Literal, Optional

# Third Party
from pydantic import BaseModel


class FileNode(BaseModel):
    """A single path from the repository inventory."""

    path: str  # e.g. "src/foo/__init__.py"
    kind: Literal["file", "dir"]
    size: Optional[int] = None  # bytes (None for directories)
