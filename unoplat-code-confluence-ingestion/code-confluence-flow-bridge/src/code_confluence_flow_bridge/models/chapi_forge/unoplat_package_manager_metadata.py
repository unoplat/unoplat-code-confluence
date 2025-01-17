# Standard Library
from typing import Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_project_dependency import UnoplatProjectDependency


class UnoplatPackageManagerMetadata(BaseModel):
    dependencies: Dict[str,UnoplatProjectDependency] = Field(default_factory=dict, description="The dependencies of the project")
    package_name: Optional[str] = Field(default=None, description="The name of the package")
    programming_language: str = Field(description="The programming language of the project")
    package_manager: str = Field(description="The package manager of the project")
    programming_language_version: Optional[str] = Field(default=None, description="The version of the programming language")
    project_version: Optional[str] = Field(default=None, description="The version of the project")
    description: Optional[str] = Field(default=None, description="The description of the project")
    authors: Optional[List[str]] = Field(default=None, description="The authors of the project")
    license: Optional[str] = Field(default=None, description="The license of the project")
    entry_points: Dict[str, str] = Field(
        default_factory=dict, 
        description="Dictionary of script names to their entry points. Example: {'cli': 'package.module:main', 'serve': 'uvicorn app:main'}"
    )
    # New fields for additional metadata
    homepage: Optional[str] = Field(
        default=None,
        description="The homepage URL of the project"
    )
    repository: Optional[str] = Field(
        default=None,
        description="The repository URL of the project"
    )
    documentation: Optional[str] = Field(
        default=None,
        description="The documentation URL of the project"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="List of keywords/tags for the project"
    )
    maintainers: List[str] = Field(
        default_factory=list,
        description="List of project maintainers"
    )
    readme: Optional[str] = Field(
        default=None,
        description="Path to or content of the project's README file"
    )
    