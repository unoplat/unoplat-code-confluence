"""File model for representing individual source code files."""

from typing import List, Optional, Union

from pydantic import BaseModel, Field
from unoplat_code_confluence_commons.base_models import (
    Detection,
    PythonStructuralSignature,
    TypeScriptStructuralSignature,
)


class UnoplatFile(BaseModel):
    """Represents individual source code files."""
    
    file_path: str = Field(description="Absolute file path")
    checksum: Optional[str] = Field(
        default=None, 
        description="Optional content checksum for change tracking"
    )
    structural_signature: Optional[
        Union[PythonStructuralSignature, TypeScriptStructuralSignature]
    ] = Field(
        default=None,
        description="Language-specific structural signature capturing the high-level outline of the file",
    )
    imports: List[str] = Field(
        default_factory=list,
        description="List of imports in the file"
    )
    
    custom_features_list: Optional[List[Detection]] = Field(
        default=None,
        description="List of custom features detected in the file"
    )
    
    has_data_model: bool = Field(
        default=False,
        description="True if file contains classes that are data models (e.g., @dataclass)"
    )