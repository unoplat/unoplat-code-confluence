"""Import information model."""

from typing import List

from pydantic import BaseModel, Field


class ImportInfo(BaseModel):
    """Information about import statements in a file."""
    start_line: int = Field(..., description="Starting line number of import block")
    end_line: int = Field(..., description="Ending line number of import block")
    imports: List[str] = Field(..., description="Array of import statement strings")