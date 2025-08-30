"""Pydantic models for codebase analysis output."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ──────────────────────────────────────────────
# 🔄 Extended Enums
# ──────────────────────────────────────────────


class CodebaseType(str, Enum):
    """Type of codebase."""

    APPLICATION = "application"
    LIBRARY = "library"


# ──────────────────────────────────────────────
# 🔄 Supporting Models
# ──────────────────────────────────────────────


class PackageManagerOutput(BaseModel):
    """Package manager configuration details."""

    package_type: str = Field(..., description="Package manager type")
    model_config = ConfigDict(extra="forbid")


class KeyDirectory(BaseModel):
    """Key directory information in terms of path for source c."""

    path: str = Field(..., description="Directory path")
    description: str = Field(..., description="Description of the directory's role")

    model_config = ConfigDict(extra="forbid")


class ConfigFile(BaseModel):
    """Configuration file details."""

    path: str = Field(..., description="Configuration file path")
    purpose: str = Field(..., description="Purpose of the configuration file")

    model_config = ConfigDict(extra="forbid")


class FeatureLocationOutput(BaseModel):
    """Location where a framework feature is used."""

    file_path: str = Field(..., description="File path where feature is used")
    is_entry_point: bool = Field(..., description="Whether this feature is an entry point like http endpoint or cli command or kafka consumer etc")

    model_config = ConfigDict(extra="forbid")


class FeatureUsageOutput(BaseModel):
    """Framework feature usage details."""

    feature_name: str = Field(..., description="Name of the feature")
    description: str = Field(..., description="Description of the feature")
    locations: List[FeatureLocationOutput] = Field(
        ..., description="Locations where feature is used"
    )

    model_config = ConfigDict(extra="forbid")


class CommandKind(str, Enum):
    """Category for a development workflow command."""

    BUILD = "build"
    DEV = "dev"
    TEST = "test"
    LINT = "lint"
    TYPE_CHECK = "type_check"


class CommandSpec(BaseModel):
    """Uniform specification for any development workflow command."""

    kind: CommandKind = Field(..., description="Category of the command")
    command: str = Field(..., description="Full runnable command string")
    description: Optional[str] = Field(None, description="Short human-friendly summary")
    tool: Optional[str] = Field(
        None, description="Primary tool (e.g., pytest, eslint, mypy) if applicable"
    )
    runner: Optional[str] = Field(
        None, description="Runner/package manager (e.g., pnpm, npm, uv, poetry, make, mvn)"
    )
    config_files: List[str] = Field(
        default_factory=list, description="Relevant config files (repo-relative)"
    )
    working_directory: Optional[str] = Field(
        None, description="If different from the codebase root"
    )

    model_config = ConfigDict(extra="forbid")


class CoreFile(BaseModel):
    """Core business logic file details."""

    path: str = Field(..., description="File path")
    responsibility: Optional[str] = Field(None, description="File's responsibility (optional)")

    model_config = ConfigDict(extra="forbid")


class BusinessLogicDomain(BaseModel):
    """Business logic domain details."""

    # Optional domain name for single-codebase context
    #domain: Optional[str] = Field(None, description="Business domain (optional)")
    description: str = Field(..., description="Domain description")
    core_files: List[CoreFile] = Field(..., description="Core files for this domain")

    model_config = ConfigDict(extra="forbid")


# ──────────────────────────────────────────────
# 🔄 Main Output Models
# ──────────────────────────────────────────────


class CodebaseMetadataOutput(BaseModel):
    """Codebase metadata information."""

    codebase_type: CodebaseType = Field(..., description="Type of codebase")
    name: str = Field(..., description="Name of the codebase")
    description: str = Field(..., description="Description of the codebase")

    model_config = ConfigDict(extra="forbid")


class ProgrammingLanguageMetadataOutput(BaseModel):
    """Programming language metadata with extended package manager support."""

    primary_language: str = Field(..., description="Primary programming language")
    package_manager: PackageManagerOutput = Field(
        ..., description="Package manager details"
    )
    version_requirement: Optional[str] = Field(
        None, description="Language version requirement"
    )

    model_config = ConfigDict(extra="forbid")


class ProjectStructure(BaseModel):
    """Project structure information."""

    #root_directory: str = Field(..., description="Root directory path only present if it is a application codebase")
    key_directories: List[KeyDirectory] = Field(..., description="Important code/test/migrations/assets dirs")
    config_files: List[ConfigFile] = Field(..., description="Configuration files - linter,test,package manager, deployment config files etc")

    model_config = ConfigDict(extra="forbid")


class FrameworkLibraryOutput(BaseModel):
    """Framework or library usage information."""

    name: str = Field(..., description="Framework/library name")
    description: str = Field(..., description="Description")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    features_used: List[FeatureUsageOutput] = Field(..., description="Features used")
    model_config = ConfigDict(extra="forbid")


class DevelopmentWorkflow(BaseModel):
    """Development workflow configuration with a unified command list."""

    commands: List[CommandSpec] = Field(
        ..., description="Unified list of workflow commands"
    )
    model_config = ConfigDict(extra="forbid")


class AgentMdOutput(BaseModel):
    """Complete codebase analysis output matching the JSON specification."""

    codebase_metadata: CodebaseMetadataOutput = Field(
        ..., description="Codebase metadata"
    )
    programming_language_metadata: ProgrammingLanguageMetadataOutput = Field(
        ..., description="Programming language metadata"
    )
    project_structure: ProjectStructure = Field(..., description="Project structure")
    major_frameworks_and_libraries: List[FrameworkLibraryOutput] = Field(
        ..., description="Major frameworks and libraries used to do the most of functionality of the application."
    )
    development_workflow: DevelopmentWorkflow = Field(
        ..., description="Development workflow configuration including build, test, lint commands "
    )
    critical_business_logic: BusinessLogicDomain = Field(
        ..., description="Critical business logic domains"
    )

    model_config = ConfigDict(extra="forbid")
