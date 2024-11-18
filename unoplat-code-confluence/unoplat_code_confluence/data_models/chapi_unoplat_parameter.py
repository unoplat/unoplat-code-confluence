# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, Field


class Parameter(BaseModel):
    type_value: Optional[str] = Field(default=None, alias="TypeValue")
    type_type: Optional[str] = Field(default=None, alias="TypeType")
