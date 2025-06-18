"""Structural signature model."""

from typing import List, Optional

from pydantic import BaseModel, Field

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.class_info import ClassInfo
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.function_info import FunctionInfo
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.variable_info import VariableInfo


class StructuralSignature(BaseModel):
    """
    Structural signature of a source code file.
    
    This model captures the high-level structure and outline of a source file,
    including module-level constructs, functions, classes, and their
    positions within the file.
    """
    module_docstring: Optional[str] = Field(None, description="Module-level docstring")
    global_variables: List[VariableInfo] = Field(default_factory=list, description="Module-level variables")
    functions: List[FunctionInfo] = Field(default_factory=list, description="Module-level functions")
    classes: List[ClassInfo] = Field(default_factory=list, description="Class definitions")