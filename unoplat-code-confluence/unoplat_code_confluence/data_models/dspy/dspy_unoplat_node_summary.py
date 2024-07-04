from typing import List, Optional
from pydantic import BaseModel,Field

from unoplat_code_confluence.data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary

class DspyUnoplatNodeSummary(BaseModel):
    node_name: Optional[str] = Field(default=None, alias="NodeName",description="The name of the class")
    node_summary: Optional[str] = Field(default=None, alias="NodeSummary",description="A summary of the class")
    node_objective: Optional[str] = Field(default=None, alias="NodeObjective",description="The objective of the class")
    functions_summary: Optional[List[DspyUnoplatFunctionSummary]] = Field(default=None, alias="FunctionsSummary",description="A list of functions in the class")