"""Codebase model for representing a single codebase within a repository."""

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package import (
    UnoplatPackage,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
    UnoplatPackageManagerMetadata,
)

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class UnoplatCodebase(BaseModel):
    """Represents a single codebase within a repository."""
    
    name: str = Field(description="Name of the codebase usually the root package name")
    readme: Optional[str] = Field(default=None, description="Optional codebase README")
    packages: Optional[UnoplatPackage] = Field(
        default=None, 
        description="The root package of the codebase"
    )
    package_manager_metadata: UnoplatPackageManagerMetadata = Field(
        description="The package manager metadata of the codebase"
    )
    root_packages: List[str] = Field(
        description="List of root package paths within the codebase"
    )
    codebase_path: str = Field(description="Codebase root directory path (absolute)")
    codebase_folder: str = Field(description="Codebase folder path relative to repository root")
    programming_language: Optional[Literal['python', 'java', 'go', 'typescript']] = Field(
        default=None,
        description="Programming language of the codebase"
    )
    