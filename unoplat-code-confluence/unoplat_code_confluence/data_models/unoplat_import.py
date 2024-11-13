from typing import List
from pydantic import BaseModel, Field

from typing import Optional

class ImportedName(BaseModel):
    original_name: str
    alias: Optional[str] = None

class UnoplatImport(BaseModel):
    source: str = Field(..., alias="Source")
    usage_names: List[ImportedName] = Field(default_factory=list, alias="UsageName")