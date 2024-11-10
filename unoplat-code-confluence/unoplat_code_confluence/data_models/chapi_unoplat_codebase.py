from typing import List, Optional

from pydantic import BaseModel, Field

from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

class UnoplatCodebase(BaseModel):
    packages: Optional[UnoplatPackage] = Field(default=None, alias="UnoplatPackages")
    package_manager_metadata: Optional[UnoplatPackageManagerMetadata] = Field(default=None, alias="PackageManagerMetadata")
    