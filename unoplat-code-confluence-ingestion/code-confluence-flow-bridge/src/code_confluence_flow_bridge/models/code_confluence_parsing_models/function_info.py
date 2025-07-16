"""Function information model."""

from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.variable_info import VariableInfo
else:
    # Import at runtime for Pydantic model resolution
    from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.variable_info import VariableInfo


class FunctionInfo(BaseModel):
    """Information about a function or method."""
    start_line: int = Field(..., description="Line number where the function starts")
    end_line: int = Field(..., description="Line number where the function ends")
    signature: str = Field(..., description="Complete function declaration including decorators, def/async def, parameters, return type")
    docstring: Optional[str] = Field(None, description="Function docstring")
    function_calls: List[str] = Field(default_factory=list, description="Fully-qualified names of function calls inside the function body, in order of appearance")
    nested_functions: List['FunctionInfo'] = Field(default_factory=list, description="Nested functions declarations")
    instance_variables: List['VariableInfo'] = Field(default_factory=list, description="Instance variable assignments (self.*) within this method")


# Handle self-reference
FunctionInfo.model_rebuild()