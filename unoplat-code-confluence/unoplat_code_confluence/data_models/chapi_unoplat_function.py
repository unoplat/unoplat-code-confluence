# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_annotation import \
    Annotation
from unoplat_code_confluence.data_models.chapi_unoplat_functioncall import \
    FunctionCall
from unoplat_code_confluence.data_models.chapi_unoplat_position import Position
from unoplat_code_confluence.data_models.unoplat_function_field_model import \
    UnoplatFunctionFieldModel


class ChapiUnoplatFunction(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    return_type: Optional[str] = Field(default=None, alias="ReturnType")
    function_calls: List[FunctionCall] = Field(default_factory=list, alias="FunctionCalls")
    annotations: List[Annotation] = Field(default_factory=list, alias="Annotations")
    position: Optional[Position] = Field(default=None, alias="Position",exclude=True)
    local_variables: List[UnoplatFunctionFieldModel] = Field(default_factory=list, alias="LocalVariables")
    body_hash: Optional[int] = Field(default=None, alias="BodyHash",exclude=True)
    content: Optional[str] = Field(default=None, alias="Content")

