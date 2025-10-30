"""Package manager metadata model."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_project_dependency import (
    UnoplatProjectDependency,
)


class UnoplatPackageManagerMetadata(BaseModel):
    """Comprehensive package manager and project metadata."""
    
    dependencies: Dict[str, Dict[str, UnoplatProjectDependency]] = Field(default_factory=dict, description="Dependency groups keyed by group name then package name")
    package_name: Optional[str] = Field(default=None, description="The name of the package")
    programming_language: str = Field(description="The programming language of the project")
    package_manager: str = Field(description="The package manager of the project")
    programming_language_version: Optional[str] = Field(default=None, description="The version of the programming language")
    project_version: Optional[str] = Field(default=None, description="The version of the project")
    description: Optional[str] = Field(default=None, description="The description of the project")
    authors: Optional[List[str]] = Field(default=None, description="The authors of the project")
    license: Optional[Dict[str, Any]] = Field(default=None, description="The license of the project")
    entry_points: Dict[str, str] = Field(default_factory=dict, description="Dictionary of script names to their entry points. Example: {'cli': 'package.module:main', 'serve': 'uvicorn app:main'}")
    scripts: Dict[str, str] = Field(default_factory=dict, description="Lifecycle commands from package manifests (e.g., npm scripts)")
    binaries: Dict[str, str] = Field(default_factory=dict, description="Command-to-executable mappings declared via bin/exports for CLI usage")
    # New fields for additional metadata
    homepage: Optional[str] = Field(default=None, description="The homepage URL of the project")
    repository: Optional[str] = Field(default=None, description="The repository URL of the project")
    documentation: Optional[str] = Field(default=None, description="The documentation URL of the project")
    keywords: List[str] = Field(default_factory=list, description="List of keywords/tags for the project")
    maintainers: List[str] = Field(default_factory=list, description="List of project maintainers")
    readme: Optional[str] = Field(default=None, description="Path to or content of the project's README file")
    manifest_path: Optional[str] = Field(default=None, description="Path to the package manifest relative to repository root")
    
    @field_validator('license', mode='before')
    @classmethod
    def validate_license(cls, value: Any) -> Optional[Dict[str, Any]]:
        """Validate and normalize license field which can be a string or a dict.
        
        Args:
            value: License value which can be a string like "MIT" or a dict like {"text": "MIT License"}
            
        Returns:
            Normalized license dictionary or None if not provided
        """
        if value is None:
            return None
        
        # If it's already a dict, return it as is
        if isinstance(value, dict):
            return value
        
        # If it's a string, convert it to a dict with 'text' key
        if isinstance(value, str):
            return {"text": value}
        
        # For any other type, convert to string and store as 'text'
        return {"text": str(value)}
