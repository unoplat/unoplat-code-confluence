from pydantic import BaseModel, Field
from typing import Optional, List

from unoplat_code_confluence.data_models.unoplat_import_type import ImportType



class ChapiUnoplatImport(BaseModel):
    source: Optional[str] = Field(default=None, alias="Source")
    usage_name: List[str] = Field(default_factory=list, alias="UsageName")
    import_type: Optional[ImportType] = Field(default=None, alias="ImportType")
    
    