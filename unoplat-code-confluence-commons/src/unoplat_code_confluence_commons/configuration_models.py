from typing import List, Optional

from pydantic import BaseModel, Field

from .programming_language_metadata import ProgrammingLanguageMetadata


class CodebaseConfig(BaseModel):
    """Pydantic model for codebase configuration in JSON config files."""
    codebase_folder: str  
    root_packages: Optional[list[str]] = Field(
        default=None,
        description=(
            "Relative paths (POSIX) to each root package inside codebase_folder."
        ),
    )
    programming_language_metadata: ProgrammingLanguageMetadata


class RepositorySettings(BaseModel):
    """Pydantic model for repository settings in JSON config files."""
    git_url: str
    output_path: str
    codebases: List[CodebaseConfig]