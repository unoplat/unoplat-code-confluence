
from pydantic import BaseModel, Field


class CodeConfluenceFunctionHiearchySub(BaseModel):
    codebase_name: str = Field(description="The name of the codebase",default=None)
    codebase_objective: str = Field(description="The objective of the codebase",default=None)
    package_name: str = Field(description="The name of the package",default=None)
    package_objective: str = Field(description="The objective of the package",default=None)
    class_name: str = Field(description="The name of the class",default=None)
    class_objective: str = Field(description="The objective of the class",default=None)
    function_name: str = Field(description="The name of the function",default=None)
    function_summary: str = Field(description="The summary of the function",default=None)
    relevance_score: int = Field(description="The relevance score of the function",default=None)