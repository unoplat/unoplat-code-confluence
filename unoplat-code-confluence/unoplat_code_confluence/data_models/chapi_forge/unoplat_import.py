# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType


class ImportedName(BaseModel):
    original_name: Optional[str] = None
    alias: Optional[str] = None

class UnoplatImport(BaseModel):
    source: Optional[str] = Field(default=None, alias="Source")
    usage_names: Optional[List[ImportedName]] = Field(default_factory=list, alias="UsageName")
    import_type: Optional[ImportType] = Field(default=None, alias="ImportType")
