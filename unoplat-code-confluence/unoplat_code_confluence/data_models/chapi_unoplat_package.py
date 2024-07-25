from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset


class UnoplatPackage(BaseModel):
    node_subsets: Optional[List[DspyUnoplatNodeSubset]] = Field( default_factory=list,description="List of the node subsets for the package")
    sub_packages: Optional[Dict[str, 'UnoplatPackage']] = Field( default_factory=dict,description="Dict of the sub-packages for the package")

UnoplatPackage.model_rebuild()
    