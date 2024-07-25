from typing import Dict, List, Optional
from pydantic import BaseModel,Field

from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary




class DspyUnoplatPackageSummary(BaseModel):
    package_objective: str = Field( description="The objective of the package in a concise manner")
    package_summary: str = Field( description="The detailed summary of the package")
    class_summary: List[DspyUnoplatNodeSummary] = Field( default_factory=list,description="List of the class summaries for the package")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata for the package")
    sub_packages: List['DspyUnoplatPackageSummary'] = Field( default_factory=list,description="List of the sub-packages for the package")

DspyUnoplatPackageSummary.model_rebuild()
    
