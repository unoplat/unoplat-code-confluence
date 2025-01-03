# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_annotation import ChapiAnnotation
from src.code_confluence_flow_bridge.models.chapi.chapi_function_field_model import ChapiFunctionFieldModel
from src.code_confluence_flow_bridge.models.chapi.chapi_functioncall import ChapiFunctionCall
from src.code_confluence_flow_bridge.models.chapi.chapi_parameter import ChapiParameter
from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position


class ChapiFunction(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    return_type: Optional[str] = Field(default=None, alias="ReturnType")
    function_calls: List[ChapiFunctionCall] = Field(default_factory=list, alias="FunctionCalls")
    parameters: List[ChapiParameter] = Field(default_factory=list, alias="Parameters",description="parameters of the function")
    annotations: List[ChapiAnnotation] = Field(default_factory=list, alias="Annotations")
    position: Optional[Position] = Field(default=None, alias="Position")
    local_variables: List[ChapiFunctionFieldModel] = Field(default_factory=list, alias="LocalVariables")
    body_hash: Optional[int] = Field(default=None, alias="BodyHash")
    content: Optional[str] = Field(default=None, alias="Content")