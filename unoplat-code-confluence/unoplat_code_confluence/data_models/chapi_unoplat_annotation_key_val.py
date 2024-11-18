


# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, Field


class ChapiUnoplatAnnotationKeyVal(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key",description="Key of the annotation")
    value: Optional[str] = Field(default=None, alias="Value",description="Value of the annotation")