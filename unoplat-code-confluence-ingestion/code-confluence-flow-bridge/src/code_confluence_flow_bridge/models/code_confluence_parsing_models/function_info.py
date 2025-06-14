"""Function information model."""

from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from typing import Self


class FunctionInfo(BaseModel):
    """Information about a function or method."""
    start_line: int = Field(..., description="Line number where the function starts")
    end_line: int = Field(..., description="Line number where the function ends")
    signature: str = Field(..., description="Complete function declaration including decorators, def/async def, parameters, return type")
    docstring: Optional[str] = Field(None, description="Function docstring")
    function_calls: List[str] = Field(default_factory=list, description="Fully-qualified names of function calls inside the function body, in order of appearance")
    nested_functions: List['FunctionInfo'] = Field(default_factory=list, description="Nested functions declarations")


# Handle self-reference
FunctionInfo.model_rebuild()