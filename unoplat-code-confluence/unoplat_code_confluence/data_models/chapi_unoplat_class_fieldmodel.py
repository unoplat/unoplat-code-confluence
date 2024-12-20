# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_annotation import \
    Annotation


class ClassFieldModel(BaseModel):
    type_type: Optional[str] = Field(default=None, alias="TypeType",description="Class Field Type")
    type_key: Optional[str] = Field(default=None, alias="TypeKey",description="Class Field Name")
    annotations: Optional[List[Annotation]]= Field(default=None, alias="Annotations",description="Class Field Annotation")

