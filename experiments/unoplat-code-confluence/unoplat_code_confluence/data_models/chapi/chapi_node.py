# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation
from unoplat_code_confluence.data_models.chapi.chapi_class_global_fieldmodel import ClassGlobalFieldModel
from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_import import ChapiImport
from unoplat_code_confluence.data_models.chapi.chapi_position import Position


class ChapiNode(BaseModel):
    node_name: Optional[str] = Field(default=None, alias="NodeName",description="name of the class, method, function, etc.")
    type: Optional[str] = Field(default=None, alias="Type")
    file_path: Optional[str] = Field(default=None, alias="FilePath")
    module: Optional[str] = Field(default=None, alias="Module")
    package: Optional[str] = Field(default=None, alias="Package")
    multiple_extend: Optional[list[str]] = Field(default_factory=list, alias="MultipleExtend")
    fields: Optional[List[ClassGlobalFieldModel]] = Field(default_factory=list, alias="Fields")
    extend: Optional[str] = Field(default=None, alias="Extend")
    imports: Optional[List[ChapiImport]] = Field(default_factory=list, alias="Imports")
    functions: Optional[List[ChapiFunction]] = Field(default_factory=list, alias="Functions")
    position: Optional[Position] = Field(default=None, alias="Position")
    content: Optional[str] = Field(default=None, alias="Content")
    annotations: Optional[List[ChapiAnnotation]] = Field(default_factory=list, alias="Annotations")
    