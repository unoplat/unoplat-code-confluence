# Standard Library
from typing import Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_node import \
    ChapiUnoplatNode


class UnoplatPackage(BaseModel):
    name: Optional[str] = Field(default=None,description="Name of the package")
    nodes: Optional[List[ChapiUnoplatNode]] = Field( default_factory=list,description="List of the nodes for the package")
    sub_packages: Optional[Dict[str, 'UnoplatPackage']] = Field( default_factory=dict,description="Dict of the sub-packages for the package")

UnoplatPackage.model_rebuild()
    