# Standard Library
from typing import Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_annotation import \
    Annotation
from unoplat_code_confluence.data_models.chapi_unoplat_class_fieldmodel import \
    ClassFieldModel
from unoplat_code_confluence.data_models.chapi_unoplat_function import \
    ChapiUnoplatFunction
from unoplat_code_confluence.data_models.chapi_unoplat_import import \
    ChapiUnoplatImport
from unoplat_code_confluence.data_models.chapi_unoplat_position import Position
from unoplat_code_confluence.data_models.unoplat_import import UnoplatImport
from unoplat_code_confluence.data_models.unoplat_import_type import ImportType
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import \
    UnoplatPackageManagerMetadata


class ChapiUnoplatNode(BaseModel):
    node_name: Optional[str] = Field(default=None, alias="NodeName",description="name of the class, method, function, etc.")
    type: Optional[str] = Field(default=None, alias="Type")
    file_path: Optional[str] = Field(default=None, alias="FilePath",exclude=True)
    module: Optional[str] = Field(default=None, alias="Module",exclude=True)
    package: Optional[str] = Field(default=None, alias="Package",exclude=True)
    qualified_name: Optional[str] = Field(default=None, alias="QualifiedName",exclude=True,description="name of class with absolute path")
    multiple_extend: Optional[list[str]] = Field(default_factory=list, alias="MultipleExtend")
    fields: List[ClassFieldModel] = Field(default_factory=list, alias="Fields")
    extend: Optional[str] = Field(default=None, alias="Extend")
    imports: List[ChapiUnoplatImport] = Field(default_factory=list, alias="Imports")
    functions: List[ChapiUnoplatFunction] = Field(default_factory=list, alias="Functions")
    position: Optional[Position] = Field(default=None, alias="Position",exclude=True)
    content: Optional[str] = Field(default=None, alias="Content",exclude=True)
    annotations: List[Annotation] = Field(default_factory=list, alias="Annotations")
    comments_description: Optional[str] = Field(default=None, alias="CommentsDescription",description="description of the node from comments")
    segregated_imports: Optional[Dict[ImportType,List[UnoplatImport]]] = Field(default=None, alias="SegregatedImports in terms of internal ,external ,standard and local libraries")
    dependent_internal_classes: List['ChapiUnoplatNode'] = Field(default_factory=list)

ChapiUnoplatNode.model_rebuild()