"""Variable information model."""

from pydantic import BaseModel, Field


class VariableInfo(BaseModel):
    """Information about a global variable declaration."""
    start_line: int = Field(..., description="Starting line number of variable declaration")
    end_line: int = Field(..., description="Ending line number of variable declaration")
    signature: str = Field(..., description="Complete variable declaration line(s)")