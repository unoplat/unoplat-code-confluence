from pydantic import BaseModel, Field
from typing import Optional, List
from data_models.function_call import FunctionCall
from data_models.annotation import Annotation
from data_models.position import Position
from data_models.field_model import FieldModel

class Function(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    return_type: Optional[str] = Field(default=None, alias="ReturnType")
    function_calls: List[FunctionCall] = Field(default_factory=list, alias="FunctionCalls")
    annotations: List[Annotation] = Field(default_factory=list, alias="Annotations")
    position: Optional[Position] = Field(default=None, alias="Position")
    local_variables: List[FieldModel] = Field(default_factory=list, alias="LocalVariables")
    position: Optional[Position] = Field(default=None, alias="Position")
    local_variables: List[FieldModel] = Field(default_factory=list, alias="LocalVariables")
    body_hash: Optional[int] = Field(default=None, alias="BodyHash")
    content: Optional[str] = Field(default=None, alias="Content")
    summary: Optional[str] = Field(default=None, alias="Summary")
