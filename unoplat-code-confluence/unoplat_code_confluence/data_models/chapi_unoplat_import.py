# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field


class Import(BaseModel):
    source: Optional[str] = Field(default=None, alias="Source")
    usage_name: List[str] = Field(default_factory=list, alias="UsageName")
