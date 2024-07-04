from pydantic import BaseModel, Field
from typing import Optional, List



class Import(BaseModel):
    source: Optional[str] = Field(default=None, alias="Source")
    usage_name: List[str] = Field(default_factory=list, alias="UsageName")
