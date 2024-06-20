from pydantic import BaseModel, Field
from typing import List, Optional

from data_models.chapi_unoplat_annotation import Annotation



class ClassFieldModel(BaseModel):
    type_type: Optional[str] = Field(default=None, alias="TypeType",description="Class Field Type")
    #type_value: Optional[str] = Field(default=None, alias="TypeValue",description="This is value of the field")
    type_key: Optional[str] = Field(default=None, alias="TypeKey",description="Class Field Name")
    annotations: Optional[List[Annotation]]= Field(default=None, alias="Annotations",description="Class Field Annotation")
