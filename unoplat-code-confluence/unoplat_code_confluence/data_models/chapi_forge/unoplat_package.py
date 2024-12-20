# Standard Library
# Standard Library
from typing import Dict, List, Optional

# Third Party
# Third Party
from pydantic import BaseModel, Field
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode

# First Party



class UnoplatPackage(BaseModel):
    name: Optional[str] = Field(default=None,description="Name of the package")
    nodes: Dict[str, List[UnoplatChapiForgeNode]] = Field( default_factory=dict,description="Dict of file paths to their nodes (classes/procedural code)")
    sub_packages: Optional[Dict[str, 'UnoplatPackage']] = Field( default_factory=dict,description="Dict of the sub-packages for the package")

UnoplatPackage.model_rebuild()
    