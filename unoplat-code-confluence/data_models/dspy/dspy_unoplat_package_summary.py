from typing import Dict, List
from pydantic import BaseModel,Field

from data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary




class DspyUnoplatPackageNodeSummary(BaseModel):
    package_name: str = Field( description="The name of the package")
    class_summary: List[DspyUnoplatNodeSummary] = Field( description="List of the class summaries for the package")


class DspyUnoplatPackageSummary(BaseModel):
    package_summary_dict: Dict[str, DspyUnoplatPackageNodeSummary] = Field( description="Dict to hold the summary of packages")
    
