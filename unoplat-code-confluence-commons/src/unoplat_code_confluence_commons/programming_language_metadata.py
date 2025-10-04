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


class ProgrammingLanguageMetadata(BaseModel):
    language: ProgrammingLanguage
    package_manager: Optional[PackageManagerType] = None
    language_version: Optional[str] = None
    manifest_path: Optional[str] = None
    project_name: Optional[str] = None