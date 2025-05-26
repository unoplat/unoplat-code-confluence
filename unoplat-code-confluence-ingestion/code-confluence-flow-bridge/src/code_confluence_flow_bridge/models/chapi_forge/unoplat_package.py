# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_file import UnoplatFile

from typing import Dict, Optional

# Third Party
from pydantic import BaseModel, Field


class UnoplatPackage(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the package")
    files: Dict[str, UnoplatFile] = Field(default_factory=dict, description="Dict of file paths to file objects")
    sub_packages: Optional[Dict[str, "UnoplatPackage"]] = Field(default_factory=dict, description="Dict of the sub-packages for the package")


UnoplatPackage.model_rebuild()
