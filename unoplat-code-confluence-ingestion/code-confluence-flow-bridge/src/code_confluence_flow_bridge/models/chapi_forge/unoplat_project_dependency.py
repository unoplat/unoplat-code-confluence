# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_version import UnoplatVersion


class UnoplatProjectDependency(BaseModel):
    version: UnoplatVersion = Field(description="Version of the dependency")
    group: Optional[str] = Field(default=None, description="Group of the dependency (e.g. dev, test)")
    extras: Optional[List[str]] = Field(default=None, description="Extra features or options for the dependency")
    source: Optional[str] = Field(default=None, description="Source of the dependency (e.g. git, pypi)")
    source_url: Optional[str] = Field(default=None, description="URL of the dependency source")
    source_reference: Optional[str] = Field(default=None, description="Reference (e.g. commit hash, branch) for source")
    subdirectory: Optional[str] = Field(default=None, description="Subdirectory within source")
    