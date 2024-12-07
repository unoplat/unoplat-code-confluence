# Standard Library
from typing import Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_forge.unoplat_project_dependency import \
    UnoplatProjectDependency


class UnoplatPackageManagerMetadata(BaseModel):
    dependencies: Dict[str,UnoplatProjectDependency] = Field(default_factory=dict, description="The dependencies of the project")
    package_name: Optional[str] = Field(default=None, description="The name of the package")
    programming_language: str = Field(description="The programming language of the project")
    package_manager: str = Field(description="The package manager of the project")
    programming_language_version: Optional[Dict[str,str]] = Field(default=None, description="The version of the programming language")
    project_version: Optional[str] = Field(default=None, description="The version of the project")
    description: Optional[str] = Field(default=None, description="The description of the project")
    authors: Optional[List[str]] = Field(default=None, description="The authors of the project")
    license: Optional[str] = Field(default=None, description="The license of the project")
    entry_points: Dict[str, str] = Field(
        default_factory=dict, 
        description="Dictionary of script names to their entry points. Example: {'cli': 'package.module:main', 'serve': 'uvicorn app:main'}"
    )