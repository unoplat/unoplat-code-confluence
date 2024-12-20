# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, Field


class UnoplatFunctionFieldModel(BaseModel):
    type_value: Optional[str] = Field(default=None, alias="TypeValue",description="function field name")
    type_type: Optional[str] = Field(default=None, alias="TypeType",description="function field type. Can be incorrect sometime if variable is returned without declaration. So refer content attribute too to understand better.")

