"""Pydantic models for file structural signatures."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ImportInfo(BaseModel):
    """Information about import statements in a file."""
    start_line: int = Field(..., description="Starting line number of import block")
    end_line: int = Field(..., description="Ending line number of import block")
    imports: List[str] = Field(..., description="Array of import statement strings")


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


class ClassInfo(BaseModel):
    """Information about a class definition."""
    start_line: int = Field(..., description="Line number where the class starts")
    end_line: int = Field(..., description="Line number where the class ends")
    signature: str = Field(..., description="Complete class declaration including decorators and inheritance")
    docstring: Optional[str] = Field(None, description="Class docstring")
    class_variables: List[VariableInfo] = Field(default_factory=list, description="Class-level variables")
    methods: List[FunctionInfo] = Field(default_factory=list, description="Class methods")
    nested_classes: List['ClassInfo'] = Field(default_factory=list, description="Nested class definitions")


class StructuralSignature(BaseModel):
    """
    Structural signature of a source code file.
    
    This model captures the high-level structure and outline of a source file,
    including module-level constructs, imports, functions, classes, and their
    positions within the file.
    """
    module_docstring: Optional[str] = Field(None, description="Module-level docstring")
    imports: Optional[ImportInfo] = Field(default=None, description="Import statements block")
    global_variables: List[VariableInfo] = Field(default_factory=list, description="Module-level variables")
    functions: List[FunctionInfo] = Field(default_factory=list, description="Module-level functions")
    classes: List[ClassInfo] = Field(default_factory=list, description="Class definitions")
    
    # Additional metadata
    total_lines: Optional[int] = Field(None, description="Total number of lines in the file")
    has_main_block: bool = Field(False, description="Whether the file has if __name__ == '__main__' block")
    encoding: Optional[str] = Field("utf-8", description="File encoding")


# Update forward references for nested classes
ClassInfo.model_rebuild()