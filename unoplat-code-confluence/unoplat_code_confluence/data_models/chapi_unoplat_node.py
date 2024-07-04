from pydantic import BaseModel, Field
from typing import Optional, List
from unoplat_code_confluence.data_models.chapi_unoplat_annotation import Annotation
from unoplat_code_confluence.data_models.chapi_unoplat_class_fieldmodel import ClassFieldModel
from unoplat_code_confluence.data_models.chapi_unoplat_import import Import
from unoplat_code_confluence.data_models.chapi_unoplat_function import Function
from unoplat_code_confluence.data_models.chapi_unoplat_position import Position



class Node(BaseModel):
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
    content: Optional[str] = Field(default=None, alias="Content")
    annotations: List[Annotation] = Field(default_factory=list, alias="Annotations")
