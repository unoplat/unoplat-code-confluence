from pydantic import BaseModel, Field
from typing import Optional, List

from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation
from unoplat_code_confluence.data_models.chapi.chapi_position import Position

class ClassGlobalFieldMetadata(BaseModel):
    class_field_type: Optional[str] = Field(default=None, alias="Type",description="Class Field Type")
    class_field_value: Optional[str] = Field(default=None,alias="DefaultValue",description="Class Variable Value")
    annotations: Optional[List[ChapiAnnotation]]= Field(default=None, alias="Annotations",description="Class Field Annotation")
    position: Optional[Position] = Field(default=None, alias="Position",description="Class Field Position")