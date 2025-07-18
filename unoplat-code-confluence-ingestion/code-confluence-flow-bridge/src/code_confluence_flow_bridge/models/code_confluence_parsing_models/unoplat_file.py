"""File model for representing individual source code files."""

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.structural_signature import (
    StructuralSignature,
)

from typing import List, Optional

from code_confluence_flow_bridge.engine.models import Detection
from pydantic import BaseModel, Field


class UnoplatFile(BaseModel):
    """Represents individual source code files."""
    
    file_path: str = Field(description="Absolute file path")
    checksum: Optional[str] = Field(
        default=None, 
        description="Optional content checksum for change tracking"
    )
    structural_signature: Optional[StructuralSignature] = Field(
        default=None,
        description="Structural signature capturing the high-level outline of the file including global variables and class variables"
    )
    imports: List[str] = Field(
        default_factory=list,
        description="List of imports in the file"
    )
    
    custom_features_list: Optional[List[Detection]] = Field(
        default=None,
        description="List of custom features detected in the file"
    )