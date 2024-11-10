from typing import Dict, Optional
from pydantic import BaseModel, Field
from typing import List
from unoplat_code_confluence.data_models.unoplat_project_dependency import UnoplatProjectDependency

class UnoplatPackageManagerMetadata(BaseModel):
    dependencies: List[UnoplatProjectDependency] = Field(default_factory=list, description="The dependencies of the project")
    package_name: Optional[str] = Field(default=None, description="The name of the package")
    programming_language: str = Field(required=True, description="The programming language of the project")
    package_manager: str = Field(required=True, description="The package manager of the project")
    programming_language_version: Optional[Dict[str,str]] = Field(default=None, description="The version of the programming language")
    project_version: Optional[str] = Field(default=None, description="The version of the project")
    description: Optional[str] = Field(default=None, description="The description of the project")
    authors: Optional[List[str]] = Field(default=None, description="The authors of the project")
    entry_point: Optional[str] = Field(default=None, description="The entry point of the project")