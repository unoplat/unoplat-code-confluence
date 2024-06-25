from pydantic import BaseModel,Field

class DspyUnoplatNodeSummary(BaseModel):
    node_name: str = Field( description="The name of the class")
    node_summary: str = Field( description="A summary of the class")