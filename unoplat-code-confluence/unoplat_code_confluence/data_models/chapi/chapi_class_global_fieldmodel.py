# Standard Library
from typing import Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation
from unoplat_code_confluence.data_models.chapi.chapi_position import Position


class ClassGlobalFieldModel(BaseModel):
    class_field_name: str = Field(..., alias="TypeValue",description="Class Field Name")
    class_field_type: Optional[str] = Field(default=None, alias="TypeType",description="Class Field Type")
    class_field_value: Optional[str] = Field(default=None,alias="DefaultValue",description="Class Variable Value")
    annotations: Optional[List[ChapiAnnotation]]= Field(default=None, alias="Annotations",description="Class Field Annotation")
    position: Optional[Position] = Field(default=None, alias="Position",description="Class Field Position")