"""Shared detection-rule models for package-manager identification."""

# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field


class Signature(BaseModel):
    """
    A test applied to the set of filenames in a directory, or to the file
    contents if 'contains' is supplied.
    """

    file: Optional[str] = None  # exact filename to look for
    contains: Optional[str] = None  # substring that must appear in that file
    contains_absence: Optional[List[str]] = (
        None  # substrings that must NOT appear in file
    )
    glob: Optional[str] = None  # shell-style wildcard pattern


class ManagerRule(BaseModel):
    """Package manager detection rule."""

    manager: str  # "poetry", "pip", "maven", …
    weight: int = 1  # for tie-breaking / confidence
    signatures: List[Signature] = Field(default_factory=list)
    workspace_field: Optional[str] = (
        None  # e.g. "workspaces" for npm, "tool.uv.workspace" for uv
    )


class LanguageRules(BaseModel):
    """Language-specific detection rules."""

    ignores: List[str]  # dir tokens to drop if not referenced
    managers: List[ManagerRule]
