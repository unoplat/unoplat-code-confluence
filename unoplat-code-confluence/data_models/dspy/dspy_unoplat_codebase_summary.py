from pydantic import BaseModel,Field

class DspyUnoplatCodebaseSummary(BaseModel):
    codebase_summary: str = Field( description="A summary of the codebase")
    codebase_name: str = Field( description="The file id of the codebase summary")