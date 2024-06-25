from typing import List, Optional

from pydantic import Field,BaseModel
from data_models.chapi_unoplat_functioncall import FunctionCall
from data_models.chapi_unoplat_parameter import Parameter


class DspyUnoplatFunctionCallSubset(BaseModel):
    node_name: Optional[str] = Field(default=None, alias="NodeName")
    function_name: Optional[str] = Field(default=None, alias="FunctionName")
    parameters: Optional[List[Parameter]] = Field(default_factory=list, alias="Parameters")