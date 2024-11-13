from typing import List, Optional

from pydantic import BaseModel, Field

from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

class UnoplatCodebase(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    repo_name: Optional[str] = Field(default=None, alias="RepoName")
    #TODO: move the below things to repository class to support mono repos.
    repo_url: Optional[str] = Field(default=None, alias="RepoURL")
    readme: Optional[str] = Field(default=None, alias = "README")
    packages: Optional[UnoplatPackage] = Field(default=None, alias="UnoplatPackages")
    package_manager_metadata: Optional[UnoplatPackageManagerMetadata] = Field(default=None, alias="PackageManagerMetadata")
    