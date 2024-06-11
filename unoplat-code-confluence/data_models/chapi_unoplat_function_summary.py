from typing import Optional
from pydantic import BaseModel, Field


class FunctionSummary(BaseModel):
    summary: Optional[str] = Field(default=None, alias="Summary",description="This should include high level summary of what function does based on function content and function metadata.")
    implementation_summary: Optional[str] = Field(default=None, alias="ImplementationSummary",description="This should include implementation details of the function in a step by step fashion with precise functional arguments and fields used to perform the operation. use all metadata shared for the function to answer .")
    
    