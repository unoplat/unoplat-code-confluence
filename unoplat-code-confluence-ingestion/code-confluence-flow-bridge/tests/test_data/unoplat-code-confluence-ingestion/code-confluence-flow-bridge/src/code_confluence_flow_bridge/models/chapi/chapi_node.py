# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_annotation import (
    ChapiAnnotation,
)
from src.code_confluence_flow_bridge.models.chapi.chapi_class_global_fieldmodel import (
    ClassGlobalFieldModel,
)
from src.code_confluence_flow_bridge.models.chapi.chapi_function import ChapiFunction
from src.code_confluence_flow_bridge.models.chapi.chapi_import import ChapiImport
from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position

from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field


class ChapiNode(BaseModel):
    """Represents a node in the code structure (class, function, etc.)."""
    
    node_name: Optional[str] = Field(
        default=None, 
        alias="NodeName", 
        description="name of the class, method, function, etc."
    )
    type: Optional[str] = Field(default=None, alias="Type")
    file_path: Optional[str] = Field(default=None, alias="FilePath")
    module: Optional[str] = Field(default=None, alias="Module")
    package: Optional[str] = Field(default=None, alias="Package")
    multiple_extend: Optional[List[str]] = Field(
        default_factory=lambda: [], 
        alias="MultipleExtend"
    )
    fields: Optional[List[ClassGlobalFieldModel]] = Field(
        default_factory=lambda: [], 
        alias="Fields"
    )
    extend: Optional[str] = Field(default=None, alias="Extend")
    imports: Optional[List[ChapiImport]] = Field(
        default_factory=lambda: [], 
        alias="Imports"
    )
    functions: Optional[List[ChapiFunction]] = Field(
        default_factory=lambda: [], 
        alias="Functions"
    )
    position: Optional[Position] = Field(default=None, alias="Position")
    content: Optional[str] = Field(default=None, alias="Content")
    annotations: Optional[List[ChapiAnnotation]] = Field(
        default_factory=lambda: [], 
        alias="Annotations"
    )
