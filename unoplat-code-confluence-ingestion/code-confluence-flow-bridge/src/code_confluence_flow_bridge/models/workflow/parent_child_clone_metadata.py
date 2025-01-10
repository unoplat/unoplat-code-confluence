
from typing import List, Optional

from pydantic import BaseModel, Field


class ParentChildCloneMetadata(BaseModel):
    repository_qualified_name: str = Field(..., description="Qualified name of the repository")
    codebase_qualified_name: Optional[List[str]] = Field(default_factory=lambda: [], description="Qualified name of the codebase")
