from pydantic import BaseModel, Field
from typing import Optional, List

from data_models.chapi_unoplat_functioncall import FunctionCall
from .chapi_unoplat_annotation import Annotation
from .chapi_unoplat_position import Position
from .chapi_unoplat_fieldmodel import FieldModel

class Function(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    return_type: Optional[str] = Field(default=None, alias="ReturnType")
    function_calls: List[FunctionCall] = Field(default_factory=list, alias="FunctionCalls")
    annotations: List[Annotation] = Field(default_factory=list, alias="Annotations")
    position: Optional[Position] = Field(default=None, alias="Position")
    local_variables: List[FieldModel] = Field(default_factory=list, alias="LocalVariables")
    body_hash: Optional[int] = Field(default=None, alias="BodyHash")
    content: Optional[str] = Field(default=None, alias="Content")
