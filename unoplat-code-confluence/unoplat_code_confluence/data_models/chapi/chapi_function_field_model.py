# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, Field


class ChapiFunctionFieldModel(BaseModel):
    function_variable_name: str = Field(default=None, alias="NameOfField",description="function field name")
    function_variable_type: Optional[str] = Field(default=None,alias="TypeOfField",description="function field type hint")
    function_variable_value: Optional[str] = Field(default=None, alias="ValueOfField",description="function field value")
    
    
