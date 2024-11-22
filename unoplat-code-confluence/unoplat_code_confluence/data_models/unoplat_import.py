# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

from unoplat_code_confluence.data_models.unoplat_import_type import ImportType


class ImportedName(BaseModel):
    original_name: str
    alias: Optional[str] = None

class UnoplatImport(BaseModel):
    source: str = Field(..., alias="Source")
    usage_names: List[ImportedName] = Field(default_factory=list, alias="UsageName")
    import_type: ImportType = Field(default=None, alias="ImportType")
