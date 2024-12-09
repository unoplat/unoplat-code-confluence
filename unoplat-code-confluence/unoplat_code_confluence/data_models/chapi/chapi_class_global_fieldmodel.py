# Standard Library
from typing import Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi.class_global_field_metadata import ClassGlobalFieldMetadata
from unoplat_code_confluence.data_models.chapi.class_global_field_scope import ClassGlobalFieldScope


class ClassGlobalFieldModel(BaseModel):
    scope: str = Field(..., alias="Scope",description="Variable Field Scope")
    class_field_name: str = Field(..., alias="TypeKey",description="Class Field Name")
    field_metadata: List[ClassGlobalFieldMetadata] = Field(..., alias="FieldMetadata",description="Class Field Metadata")
