


from typing import List, Optional

from unoplat_code_confluence.data_models.chapi_unoplat_position import Position
from unoplat_code_confluence.data_models.chapi_unoplat_parameter import Parameter
from pydantic import BaseModel, Field


class FunctionCall(BaseModel):
    package: Optional[str] = Field(default=None, alias="Package")
    type: Optional[str] = Field(default=None, alias="Type")
    node_name: Optional[str] = Field(default=None, alias="NodeName")
    function_name: Optional[str] = Field(default=None, alias="FunctionName")
    parameters: List[Parameter] = Field(default_factory=list, alias="Parameters")
    position: Optional[Position] = Field(default=None, alias="Position")
