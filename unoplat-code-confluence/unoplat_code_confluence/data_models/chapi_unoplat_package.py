from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset


class UnoplatPackage(BaseModel):
    package_dict: Optional[Dict[str,List[DspyUnoplatNodeSubset]]] = Field(default_factory=dict,alias="package_dict")
