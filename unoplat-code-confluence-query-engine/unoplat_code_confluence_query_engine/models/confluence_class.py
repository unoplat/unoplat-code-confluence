from pydantic import BaseModel, Field

class CodeConfluenceClass(BaseModel):
    class_name: str = Field(default=None, description="The name of the class")
    class_summary: str = Field(default=None, description="The summary of the class")
    class_objective: str = Field(default=None, description="The objective of the class")
    relevance_score: int = Field(default=None, description="The relevance score of the class")
