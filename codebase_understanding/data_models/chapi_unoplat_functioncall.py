


from typing import List, Optional

from data_models import Position
from data_models.chapi_unoplat_parameter import Parameter
from pydantic import BaseModel, Field


class FunctionCall(BaseModel):
    package: Optional[str] = Field(default=None, alias="Package")
    type: Optional[str] = Field(default=None, alias="Type")
    node_name: Optional[str] = Field(default=None, alias="NodeName")
    function_name: Optional[str] = Field(default=None, alias="FunctionName")
    parameters: List[Parameter] = Field(default_factory=list, alias="Parameters")
    position: Optional[Position] = Field(default=None, alias="Position")
