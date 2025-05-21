from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode

from typing import List, Optional

from pydantic import BaseModel, Field


class UnoplatFile(BaseModel):
    """Model representing a source code file in the codebase."""
    
    file_path: str = Field(..., description="Absolute path to the file")
    content: Optional[str] = Field(default=None, description="Content of the file")
    checksum: Optional[str] = Field(default=None, description="Checksum of the file content for tracking changes")
    nodes: List[UnoplatChapiForgeNode] = Field(default_factory=list, description="Nodes (classes, functions) contained in this file") 