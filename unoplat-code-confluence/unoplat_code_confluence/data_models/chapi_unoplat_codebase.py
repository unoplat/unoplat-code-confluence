# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_package import \
    UnoplatPackage


class UnoplatCodebase(BaseModel):
    packages: Optional[UnoplatPackage] = Field(default=None, alias="UnoplatPackages")
    