from pydantic import BaseModel, Field
from typing import Optional, List
from unoplat_code_confluence.data_models.chapi_unoplat_annotation import Annotation
from unoplat_code_confluence.data_models.chapi_unoplat_class_fieldmodel import ClassFieldModel
from unoplat_code_confluence.data_models.chapi_unoplat_import import Import
from unoplat_code_confluence.data_models.chapi_unoplat_function import ChapiUnoplatFunction
from unoplat_code_confluence.data_models.chapi_unoplat_position import Position



class ChapiUnoplatNode(BaseModel):
    node_name: Optional[str] = Field(default=None, alias="NodeName")
    type: Optional[str] = Field(default=None, alias="Type")
    file_path: Optional[str] = Field(default=None, alias="FilePath",exclude=True)
    module: Optional[str] = Field(default=None, alias="Module",exclude=True)
    package: Optional[str] = Field(default=None, alias="Package",exclude=True)
    multiple_extend: Optional[list[str]] = Field(default_factory=list, alias="MultipleExtend")
    fields: List[ClassFieldModel] = Field(default_factory=list, alias="Fields")
    extend: Optional[str] = Field(default=None, alias="Extend")
    imports: List[Import] = Field(default_factory=list, alias="Imports")
    functions: List[ChapiUnoplatFunction] = Field(default_factory=list, alias="Functions")
    position: Optional[Position] = Field(default=None, alias="Position",exclude=True)
    content: Optional[str] = Field(default=None, alias="Content",exclude=True)
    annotations: List[Annotation] = Field(default_factory=list, alias="Annotations")
