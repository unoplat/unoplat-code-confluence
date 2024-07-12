from typing import List, Optional

from pydantic import BaseModel, Field
from unoplat_code_confluence.data_models.chapi_unoplat_class_fieldmodel import ClassFieldModel
from unoplat_code_confluence.data_models.chapi_unoplat_import import Import
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset


class DspyUnoplatNodeSubset(BaseModel):
    node_name: Optional[str] = Field(default=None, alias="NodeName", description="This is name of the class.")
    multiple_extend: Optional[list[str]] = Field(default_factory=List, alias="MultipleExtend", description="this includes if class is inheriting multiple classes")
    fields: Optional[List[ClassFieldModel]] = Field(default_factory=List, alias="Fields", description="This includes class fields")
    extend: Optional[str] = Field(default=None, alias="Extend", description="This includes class inheritance")
    imports: Optional[List[Import]] = Field(default_factory=List, alias="Imports", description="This includes class imports which can be used to infer types of fields")
    annotations: Optional[List[DspyUnoplatAnnotationSubset]] = Field(default_factory=list, alias="Annotations")
    functions: List[DspyUnoplatFunctionSubset] = Field(default_factory=list, alias="Functions",exclude=True)
    content: Optional[str] = Field(default=None, alias="Content",exclude=True)
