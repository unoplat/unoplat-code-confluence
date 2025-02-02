# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_annotation import ChapiAnnotation
from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position

from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field


class ClassGlobalFieldModel(BaseModel):
    class_field_name: str = Field(..., alias="TypeValue", description="Class Field Name")
    class_field_type: Optional[str] = Field(default=None, alias="TypeType", description="Class Field Type")
    class_field_value: Optional[str] = Field(default=None, alias="DefaultValue", description="Class Variable Value")
    annotations: Optional[List[ChapiAnnotation]] = Field(default=None, alias="Annotations", description="Class Field Annotation")
    position: Optional[Position] = Field(default=None, alias="Position", description="Class Field Position")
