from typing import Optional
from pydantic import BaseModel,Field

from data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageSummary

class DspyUnoplatCodebaseSummary(BaseModel):
    codebase_summary: Optional[str] = Field(default=None, description="A summary of the codebase")
    codebase_name: Optional[str] = Field( default=None,description="The file id of the codebase summary")
    codebase_package: Optional[DspyUnoplatPackageSummary] = Field(default=None,description="A summary of the codebase package")