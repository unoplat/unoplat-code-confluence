# Standard Library
from typing import Dict, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.forge_summary.forge_unoplat_package_summary import DspyUnoplatPackageSummary


class ForgeUnoplatCodebaseSummary(BaseModel):
    codebase_summary: Optional[str] = Field(default=None, description="A summary of the codebase")
    codebase_objective: Optional[str] = Field(default=None, description="The objective of the codebase")
    metadata: Optional[dict] = Field(default=None, description="The metadata of the codebase")
    codebase_name: Optional[str] = Field( default=None,description="The file id of the codebase summary")
    codebase_package: Optional[Dict[str,DspyUnoplatPackageSummary]] = Field(default_factory=dict,description="A summary of the codebase package")