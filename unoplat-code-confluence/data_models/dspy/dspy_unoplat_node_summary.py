from typing import List
from pydantic import BaseModel,Field

from data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary

class DspyUnoplatNodeSummary(BaseModel):
    node_name: str = Field( description="The name of the class")
    node_summary: str = Field( description="A summary of the class")
    functions_summary: List[DspyUnoplatFunctionSummary] = Field( description="A list of functions in the class")