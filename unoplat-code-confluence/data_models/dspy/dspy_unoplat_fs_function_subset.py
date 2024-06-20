from typing import List, Optional

from pydantic import BaseModel, Field
from data_models.chapi_unoplat_annotation import Annotation
from data_models.chapi_unoplat_class_fieldmodel import FieldModel
from data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset
from data_models.dspy.dspy_unoplat_fs_function_call_subset import DspyUnoplatFunctionCallSubset

    
class DspyUnoplatFunctionSubset(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    return_type: Optional[str] = Field(default=None, alias="ReturnType")
    function_calls: List[DspyUnoplatFunctionCallSubset] = Field(default_factory=list, alias="FunctionCalls")
    annotations: List[DspyUnoplatAnnotationSubset] = Field(default_factory=list, alias="Annotations")
    local_variables: List[FieldModel] = Field(default_factory=list, alias="LocalVariables")
    content: Optional[str] = Field(default=None, alias="Content")
        
    