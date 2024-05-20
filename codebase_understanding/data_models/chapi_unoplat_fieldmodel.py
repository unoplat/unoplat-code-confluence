from pydantic import BaseModel, Field
from typing import Optional



class FieldModel(BaseModel):
    type_type: Optional[str] = Field(default=None, alias="TypeType")
    type_value: Optional[str] = Field(default=None, alias="TypeValue")
    type_key: Optional[str] = Field(default=None, alias="TypeKey")
