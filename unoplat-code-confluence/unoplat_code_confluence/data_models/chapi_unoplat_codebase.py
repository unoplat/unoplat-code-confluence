from typing import List, Optional

from pydantic import BaseModel, Field

from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage


class UnoplatCodebase(BaseModel):
    packages: Optional[UnoplatPackage] = Field(default=None, alias="UnoplatPackages")
    