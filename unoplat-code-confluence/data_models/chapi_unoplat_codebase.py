from typing import List, Optional

from pydantic import BaseModel, Field

from data_models.chapi_unoplat_package import UnoplatPackage


class UnoplatCodebase(BaseModel):
    packages: List[UnoplatPackage] = Field(default_factory=list, alias="Packages")
    summary: Optional[str] = Field(default=None, alias="Summary")