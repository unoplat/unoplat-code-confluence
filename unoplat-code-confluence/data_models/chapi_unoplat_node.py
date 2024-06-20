from pydantic import Field
from typing import Optional, List
from data_models.chapi_unoplat_annotation import Annotation
from data_models.chapi_unoplat_class_summary import ClassSummary
from data_models.chapi_unoplat_class_fieldmodel import ClassFieldModel
from data_models.chapi_unoplat_import import Import
from data_models.chapi_unoplat_function import Function
from data_models.chapi_unoplat_position import Position
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset


class Node(DspyUnoplatNodeSubset):
    node_name: Optional[str] = Field(default=None, alias="NodeName")
    type: Optional[str] = Field(default=None, alias="Type")
    file_path: Optional[str] = Field(default=None, alias="FilePath")
    module: Optional[str] = Field(default=None, alias="Module")
    package: Optional[str] = Field(default=None, alias="Package")
    multiple_extend: Optional[bool] = Field(default=None, alias="MultipleExtend")
    fields: List[ClassFieldModel] = Field(default_factory=list, alias="Fields")
    extend: Optional[str] = Field(default=None, alias="Extend")
    imports: List[Import] = Field(default_factory=list, alias="Imports")
    functions: List[Function] = Field(default_factory=list, alias="Functions")
    position: Optional[Position] = Field(default=None, alias="Position")
    summary: Optional[ClassSummary] = Field(default=None, alias="Summary")
    content: Optional[str] = Field(default=None, alias="Content")
    annotations: List[Annotation] = Field(default_factory=list, alias="Annotations")
