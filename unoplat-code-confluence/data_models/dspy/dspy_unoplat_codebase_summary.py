from pydantic import BaseModel,Field

from data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageSummary

class DspyUnoplatCodebaseSummary(BaseModel):
    codebase_summary: str = Field( description="A summary of the codebase")
    codebase_name: str = Field( description="The file id of the codebase summary")
    codebase_package: DspyUnoplatPackageSummary = Field( description="A summary of the codebase package")