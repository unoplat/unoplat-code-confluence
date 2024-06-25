from typing import Dict
from pydantic import BaseModel,Field


class DspyUnoplatPackageSummary(BaseModel):
    package_summary_dict: Dict[str, str] = Field( description="Dict to hold the summary of packages")
    
