# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, Field


class ChapiParameter(BaseModel):
    type_value: Optional[str] = Field(default=None,description="parameter name", alias="TypeValue")
    type_type: Optional[str] = Field(default=None,description="parameter type", alias="TypeType")
    default_value: Optional[str] = Field(default=None,description="parameter default value", alias="DefaultValue")