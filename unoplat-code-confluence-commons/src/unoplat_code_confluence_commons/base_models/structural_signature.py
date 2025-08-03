"""Pydantic models for file structural signatures."""

from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass


class VariableInfo(BaseModel):
    """Information about a global variable declaration."""
    start_line: int = Field(..., description="Starting line number of variable declaration")
    end_line: int = Field(..., description="Ending line number of variable declaration")
    signature: str = Field(..., description="Complete variable declaration line(s)")


class FunctionInfo(BaseModel):
    """Information about a function or method."""
    start_line: int = Field(..., description="Line number where the function starts")
    end_line: int = Field(..., description="Line number where the function ends")
    signature: str = Field(..., description="Complete function declaration including decorators, def/async def, parameters, return type")
    docstring: Optional[str] = Field(None, description="Function docstring")
    function_calls: List[str] = Field(default_factory=list, description="Fully-qualified names of function calls inside the function body, in order of appearance")
    nested_functions: List['FunctionInfo'] = Field(default_factory=list, description="Nested functions declarations")
    instance_variables: List['VariableInfo'] = Field(default_factory=list, description="Instance variable assignments (self.*) within this method")


class ClassInfo(BaseModel):
    """Information about a class definition."""
    start_line: int = Field(..., description="Line number where the class starts")
    end_line: int = Field(..., description="Line number where the class ends")
    signature: str = Field(..., description="Complete class declaration including decorators and inheritance")
    docstring: Optional[str] = Field(None, description="Class docstring")
    vars: List[VariableInfo] = Field(default_factory=list, description="Class and instance variables")
    methods: List[FunctionInfo] = Field(default_factory=list, description="Class methods")
    nested_classes: List['ClassInfo'] = Field(default_factory=list, description="Nested class declarations")


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


# Handle self-references for nested types
FunctionInfo.model_rebuild()
ClassInfo.model_rebuild()