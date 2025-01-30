from pydantic import BaseModel, Field

class CodeConfluencePackage(BaseModel):
    package_name: str = Field(default=None, description="The name of the package")
    package_summary: str = Field(default=None, description="The summary of the package")
    package_objective: str = Field(default=None, description="The objective of the package")
    relevance_score: int = Field(default=None, description="The relevance score of the package")