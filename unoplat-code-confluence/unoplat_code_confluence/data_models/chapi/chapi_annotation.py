# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, Field


# First Party
from unoplat_code_confluence.data_models.chapi.chapi_annotation_key_val import ChapiAnnotationKeyVal
from unoplat_code_confluence.data_models.chapi.chapi_position import Position




class ChapiAnnotation(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    key_values: Optional[list[ChapiAnnotationKeyVal]] = Field(default_factory=list, alias="KeyValues")
    position: Optional[Position] = Field(default=None, alias="Position")
