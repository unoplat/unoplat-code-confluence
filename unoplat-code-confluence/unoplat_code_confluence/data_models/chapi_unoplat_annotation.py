from unoplat_code_confluence.data_models.chapi_unoplat_annotation_key_val import ChapiUnoplatAnnotationKeyVal
from unoplat_code_confluence.data_models.chapi_unoplat_position import Position
from pydantic import  BaseModel, Field
from typing import Optional



class Annotation(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    key_values: Optional[list[ChapiUnoplatAnnotationKeyVal]] = Field(default_factory=list, alias="KeyValues")
    position: Optional[Position] = Field(default=None, alias="Position")
