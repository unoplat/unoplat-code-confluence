from pydantic import BaseModel,Field

from unoplat_code_confluence.data_models.dspy.dspy_o_function_summary import DspyFunctionSummary

class DspyUnoplatFunctionSummary(BaseModel):
    function_name: str = Field( alias="FunctionName", description="The name of the function")
    function_summary: DspyFunctionSummary = Field( alias="FunctionSummary", description="A summary of the function")