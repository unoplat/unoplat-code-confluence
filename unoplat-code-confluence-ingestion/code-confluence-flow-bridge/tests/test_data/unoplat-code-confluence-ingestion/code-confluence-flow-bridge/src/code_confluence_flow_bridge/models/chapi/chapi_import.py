# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field


class ChapiImport(BaseModel):
    source: Optional[str] = Field(default=None, alias="Source")
    usage_name: Optional[List[str]] = Field(default_factory=list, alias="UsageName")
