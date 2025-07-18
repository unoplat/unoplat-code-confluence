"""Class information model."""

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.function_info import (
    FunctionInfo,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.variable_info import (
    VariableInfo,
)

from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass


class ClassInfo(BaseModel):
    """Information about a class definition."""
    start_line: int = Field(..., description="Line number where the class starts")
    end_line: int = Field(..., description="Line number where the class ends")
    signature: str = Field(..., description="Complete class declaration including decorators and inheritance")
    docstring: Optional[str] = Field(None, description="Class docstring")
    vars: List[VariableInfo] = Field(default_factory=list, description="Class and instance variables")
    methods: List[FunctionInfo] = Field(default_factory=list, description="Class methods")
    nested_classes: List['ClassInfo'] = Field(default_factory=list, description="Nested class declarations")


# Handle self-reference
ClassInfo.model_rebuild()