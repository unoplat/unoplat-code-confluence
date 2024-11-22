# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_package import \
    UnoplatPackage
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import \
    UnoplatPackageManagerMetadata


class UnoplatCodebase(BaseModel):
    name: str = Field(description="Name of the codebase usually the root package name")
    readme: Optional[str] = Field(default=None)
    packages: Optional[UnoplatPackage] = Field(default=None)
    package_manager_metadata: UnoplatPackageManagerMetadata = Field(description="The package manager metadata of the codebase")
    local_path: str = Field(description="Local path of the codebase")
