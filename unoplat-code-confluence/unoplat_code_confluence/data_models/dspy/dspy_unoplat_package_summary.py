from typing import Dict, List, Optional
from pydantic import BaseModel,Field

from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary




class DspyUnoplatPackageNodeSummary(BaseModel):
    package_objective: str = Field( description="The objective of the package in a concise manner")
    package_summary: str = Field( description="The detailed summary of the package")
    class_summary: List[DspyUnoplatNodeSummary] = Field( default_factory=list,description="List of the class summaries for the package")


class DspyUnoplatPackageSummary(BaseModel):
    package_summary_dict: Optional[Dict[str, DspyUnoplatPackageNodeSummary]] = Field(default_factory=dict,description="Dict to hold the summary of packages")
    
