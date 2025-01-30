# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import UnoplatPackage
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

from typing import Optional

# Third Party
from pydantic import BaseModel, Field


class UnoplatCodebase(BaseModel):
    name: str = Field(description="Name of the codebase usually the root package name")
    readme: Optional[str] = Field(default=None)
    packages: Optional[UnoplatPackage] = Field(default=None)
    package_manager_metadata: UnoplatPackageManagerMetadata = Field(description="The package manager metadata of the codebase")
    local_path: str = Field(description="Local path of the codebase")
    source_directory: str = Field(description="Source directory of the codebase")
