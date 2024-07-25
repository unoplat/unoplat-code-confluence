from typing import Optional
from pydantic import BaseModel,Field

from unoplat_code_confluence.data_models.dspy.dspy_o_function_summary import DspyFunctionSummary

class DspyUnoplatFunctionSummary(BaseModel):
    function_name: str = Field( alias="FunctionName", description="The name of the function")
    function_summary: DspyFunctionSummary = Field( alias="FunctionSummary", description="A summary of the function")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata for the function")