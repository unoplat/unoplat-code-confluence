"""Position model for source code location information."""

from typing import Optional

from pydantic import BaseModel, Field


class Position(BaseModel):
    """Represents source code location information."""

    start_line: Optional[int] = Field(default=None, alias="StartLine")
    stop_line: Optional[int] = Field(default=None, alias="StopLine")
