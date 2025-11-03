"""Data model position information."""

from typing import Dict, Tuple

from pydantic import BaseModel, Field


class DataModelPosition(BaseModel):
    """Represents positions of data models detected in a file."""

    positions: Dict[str, Tuple[int, int]] = Field(
        default_factory=dict,
        description="Map of data model names to their (start_position, end_position) in the file",
    )