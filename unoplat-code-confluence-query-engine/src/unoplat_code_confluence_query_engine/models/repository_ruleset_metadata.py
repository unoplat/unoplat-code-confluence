from pydantic import BaseModel, Field


class CodebaseMetadata(BaseModel):
    codebase_name: str = Field(
        description="The name/identifier of the codebase (relative path from repository root)"
    )
    codebase_path: str = Field(
        description="The absolute file system path to the codebase root directory"
    )
    codebase_programming_language: str = Field(
        description="The programming language of the codebase"
    )
    
    codebase_package_manager: str = Field(
        description="The package manager of the codebase"
    )


class RepositoryRulesetMetadata(BaseModel):
    repository_qualified_name: str = Field(
        description="The qualified name of the repository"
    )
    codebase_metadata: list[CodebaseMetadata] = Field(
        description="The metadata of the codebases"
    )
