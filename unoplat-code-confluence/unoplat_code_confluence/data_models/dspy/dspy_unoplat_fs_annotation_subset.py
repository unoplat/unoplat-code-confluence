



from typing import Optional
from pydantic import BaseModel, Field

from data_models.chapi_unoplat_annotation_key_val import ChapiUnoplatAnnotationKeyVal


class DspyUnoplatAnnotationSubset(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    key_values: Optional[list[ChapiUnoplatAnnotationKeyVal]] = Field(default_factory=list, alias="KeyValues")