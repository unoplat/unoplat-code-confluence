"""Version constraint model."""

from typing import Optional

from pydantic import BaseModel, Field


class UnoplatVersion(BaseModel):
    """Flexible version constraint representation."""
    
    specifier: Optional[str] = Field(
        default=None, 
        description="Version specifier string (e.g., '>=1.0.0,<2.0.0')"
    )
    minimum_version: Optional[str] = Field(
        default=None, 
        description="Minimum allowed version"
    )
    maximum_version: Optional[str] = Field(
        default=None, 
        description="Maximum allowed version"
    )
    current_version: Optional[str] = Field(
        default=None, 
        description="Currently installed/used version"
    )