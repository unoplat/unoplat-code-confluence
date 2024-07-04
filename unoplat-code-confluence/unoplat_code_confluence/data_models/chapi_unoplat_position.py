
from typing import Optional
from pydantic import BaseModel, Field


class Position(BaseModel):
    start_line: Optional[int] = Field(default=None, alias="StartLine")
    start_line_position: Optional[int] = Field(default=None, alias="StartLinePosition")
    stop_line: Optional[int] = Field(default=None, alias="StopLine")
    stop_line_position: Optional[int] = Field(default=None, alias="StopLinePosition")