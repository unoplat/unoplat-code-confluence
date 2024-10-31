from typing import Optional
from pydantic import BaseModel,Field


class DspyUnoplatFunctionSummary(BaseModel):
    function_name: str = Field( alias="FunctionName", description="The name of the function")
    objective: Optional[str] = Field(default=None, alias="Objective",description="This should include high level objective of what function does based on function content and function metadata. Should not be more than 3 lines.")
    implementation_summary: Optional[str] = Field(default=None, alias="ImplementationSummary",description="This should include implementation details of the function. make sure if this function makes internal calls to other functions of same class and to external calls to other classes/libs is also covered. Use all metadata shared for the function to answer .")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata for the function")