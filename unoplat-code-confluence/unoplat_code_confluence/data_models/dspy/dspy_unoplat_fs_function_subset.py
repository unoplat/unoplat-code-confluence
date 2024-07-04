from typing import List, Optional

from pydantic import BaseModel, Field
from data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset
from data_models.dspy.dspy_unoplat_fs_function_call_subset import DspyUnoplatFunctionCallSubset
from data_models.unoplat_function_field_model import UnoplatFunctionFieldModel

    
class DspyUnoplatFunctionSubset(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    return_type: Optional[str] = Field(default=None, alias="ReturnType")
    function_calls: Optional[List[DspyUnoplatFunctionCallSubset]] = Field(default_factory=list, alias="FunctionCalls")
    annotations: Optional[List[DspyUnoplatAnnotationSubset]] = Field(default_factory=list, alias="Annotations")
    local_variables: Optional[List[UnoplatFunctionFieldModel]] = Field(default_factory=list, alias="LocalVariables")
    content: Optional[str] = Field(default=None, alias="Content")
        
    