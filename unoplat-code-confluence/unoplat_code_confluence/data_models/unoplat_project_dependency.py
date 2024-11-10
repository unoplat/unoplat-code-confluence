from typing import Optional, List
from pydantic import BaseModel, Field
from unoplat_code_confluence.data_models.unoplat_version import UnoplatVersion

class UnoplatProjectDependency(BaseModel):
    name: str = Field(description="Name of the dependency")
    version: UnoplatVersion = Field(description="Version of the dependency")
    group: Optional[str] = Field(default=None, description="Group of the dependency (e.g. dev, test)")
    extras: Optional[List[str]] = Field(default=None, description="Extra features or options for the dependency")
    source: Optional[str] = Field(default=None, description="Source of the dependency (e.g. git, pypi)")
    source_url: Optional[str] = Field(default=None, description="URL of the dependency source")
    source_reference: Optional[str] = Field(default=None, description="Reference (e.g. commit hash, branch) for source")
    subdirectory: Optional[str] = Field(default=None, description="Subdirectory within source")
    