"""Package model for representing packages/modules in the codebase."""

from typing import Dict, Optional

from pydantic import BaseModel, Field

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
)


class UnoplatPackage(BaseModel):
    """Represents a package/module in the codebase with hierarchical structure."""

    name: Optional[str] = Field(default=None, description="Name of the package")
    files: Dict[str, UnoplatFile] = Field(
        default_factory=dict, description="Dict of file paths to file objects"
    )
    sub_packages: Optional[Dict[str, "UnoplatPackage"]] = Field(
        default_factory=lambda: {},
        description="Dict of the sub-packages for the package",
    )


# Handle self-reference
UnoplatPackage.model_rebuild()