# Standard Library
# Standard Library
from typing import Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode


class UnoplatPackage(BaseModel):
    name: Optional[str] = Field(default=None,description="Name of the package")
    nodes: Dict[str, List[UnoplatChapiForgeNode]] = Field( default_factory=dict,description="Dict of file paths to their nodes (classes/procedural code)")
    sub_packages: Optional[Dict[str, 'UnoplatPackage']] = Field( default_factory=dict,description="Dict of the sub-packages for the package")

UnoplatPackage.model_rebuild()
    