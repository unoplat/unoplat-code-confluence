from pydantic import BaseModel, Field
from typing import Optional
class UnoplatVersion(BaseModel):
    minimum_version: Optional[str] = Field(default=None, description="The minimum version of the project")
    maximum_version: Optional[str] = Field(default=None, description="The maximum version of the project")
    current_version: Optional[str] = Field(default=None, description="The current version of the project")
