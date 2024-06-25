from typing import List, Optional

from pydantic import BaseModel, Field

from data_models.chapi_unoplat_package import UnoplatPackage


class UnoplatCodebase(BaseModel):
    packages: Optional[UnoplatPackage] = Field(default=None, alias="UnoplatPackages")
    