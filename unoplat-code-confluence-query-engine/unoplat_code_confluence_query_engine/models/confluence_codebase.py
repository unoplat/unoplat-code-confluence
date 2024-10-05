from pydantic import BaseModel, Field

class CodeConfluenceCodebase(BaseModel):
    codebase_name: str = Field(default=None, description="The name of the codebase")
    codebase_summary: str = Field(default=None, description="The summary of the codebase")
    codebase_objective: str = Field(default=None, description="The objective of the codebase")
    relevance_score: int = Field(default=None, description="The relevance score of the codebase")