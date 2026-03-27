from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"


class PackageManagerType(str, Enum):
    POETRY = "poetry"
    PIP = "pip"
    UV = "uv"
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    BUN = "bun"


class PackageManagerProvenance(str, Enum):
    LOCAL = "local"
    INHERITED = "inherited"


class WorkspaceOrchestratorType(str, Enum):
    TURBO = "turbo"
    NX = "nx"


class ProgrammingLanguageMetadata(BaseModel):
    language: ProgrammingLanguage
    package_manager: Optional[PackageManagerType] = None
    language_version: Optional[str] = None
    manifest_path: Optional[str] = None
    project_name: Optional[str] = None
    package_manager_provenance: Optional[PackageManagerProvenance] = None
    workspace_root: Optional[str] = None
    workspace_orchestrator: Optional[WorkspaceOrchestratorType] = None
    workspace_orchestrator_config_path: Optional[str] = None
