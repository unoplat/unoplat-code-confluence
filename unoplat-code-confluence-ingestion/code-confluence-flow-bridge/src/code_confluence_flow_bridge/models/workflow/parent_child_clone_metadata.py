from typing import List, Optional

from pydantic import BaseModel, Field


class ParentChildCloneMetadata(BaseModel):
    repository_qualified_name: str
    codebase_qualified_names: list[str] = Field(default_factory=list)
