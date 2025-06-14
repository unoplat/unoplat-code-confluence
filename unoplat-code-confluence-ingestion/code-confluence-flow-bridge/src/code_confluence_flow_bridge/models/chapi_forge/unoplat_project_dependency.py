# # Standard Library
# # First Party
# from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_version import UnoplatVersion
# 
# from typing import List, Optional
# 
# # Third Party
# from pydantic import BaseModel, Field
# 
# 
# class UnoplatProjectDependency(BaseModel):
#     version: UnoplatVersion = Field(default_factory=UnoplatVersion, description="Version constraint")
#     group: Optional[str] = Field(default=None, description="Group of the dependency (e.g. dev, test)")
#     extras: Optional[List[str]] = Field(default=None, description="List of extras for this dependency")
#     source: Optional[str] = Field(default=None, description="Source of the dependency (e.g. 'git', 'url', 'path')")
#     source_url: Optional[str] = Field(default=None, description="URL or path to the dependency source")
#     source_reference: Optional[str] = Field(default=None, description="Branch, tag, or commit reference")
#     subdirectory: Optional[str] = Field(default=None, description="Subdirectory within source")
#     environment_marker: Optional[str] = Field(default=None, description="PEP 508 environment marker string (e.g., python_version < '3.7')")
