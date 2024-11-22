# Standard Library
import re
from enum import Enum
from typing import Any, Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field, ValidationInfo, field_validator


class PackageManagerType(Enum):
    POETRY = "poetry"
    PIP = "pip"

    
#TODO: add pip support
class PackageManager(BaseModel):
    PYTHON: List[str] = Field(default_factory=lambda: [PackageManagerType.POETRY.value,PackageManagerType.PIP.value], frozen=True)
    #PIP = "pip"
    
#TODO: add java and javascript support
class ProgrammingLanguage(Enum):
    PYTHON = 'python'
    #JAVA = 'java'
    # JAVASCRIPT = 'JavaScript'
    # CSHARP = 'C#'
    # RUBY = 'Ruby'
    # GO = 'Go'
    # KOTLIN = 'Kotlin'
    # SWIFT = 'Swift'


class RepoConfig(BaseModel):
    download_url: str
    download_directory: str

class ProgrammingLanguageMetadata(BaseModel):
    language: ProgrammingLanguage
    package_manager: str
    language_version: Optional[str] = None

    @field_validator('package_manager')
    @classmethod
    def validate_package_manager(cls, value: str, info: ValidationInfo) -> str:
        data = info.data
        language = data.get('language')
        
        if language == ProgrammingLanguage.PYTHON:
            valid_managers = PackageManager().PYTHON
            if value not in valid_managers:
                raise ValueError(f"For Python projects, package_manager must be one of: {valid_managers}")
        return value
    
    #write a field validator on version to check if it is a valid version string this string will be used for the stdlist version init
    
    @field_validator('language_version')
    @classmethod
    def validate_version(cls, value: str, info: ValidationInfo) -> str:
        data = info.data
        language = data.get('language_version')
        if language == ProgrammingLanguage.PYTHON:
            # Check if version string matches semantic versioning format
            version_pattern = r'^\d+\.\d+\.\d+$'
            if not re.match(version_pattern, value):
                raise ValueError("Version must be in format X.Y.Z where X, Y, Z are numbers (e.g. 3.9.0)")
        return value

class CodebaseConfig(BaseModel):
    codebase_folder_name: str = Field(description="Name of the codebase folder")
    root_package_name: Optional[str] = Field(default=None,description="Root package name of the codebase. Needed for python codebases")
    programming_language_metadata: ProgrammingLanguageMetadata
    

class RepositoryConfig(BaseModel):
    git_url: str = Field(default=None,description="Git URL of the codebase")
    personal_access_token: str = Field(default=None,description="Personal Access Token for the codebase")
    codebases: List[CodebaseConfig] = Field(default_factory=list,description="List of codebases in the repository")
    markdown_output_path: str = Field(default=None,description="Path to the markdown output files")
    
    
class AppConfig(BaseModel):
    repositories: List[RepositoryConfig]
    repo: RepoConfig = Field(default=None,description="ArcGuard Repo Config",alias="archguard")
    llm_provider_config: Dict[str, Any] = Field(
        description="Configuration for the LLM provider based on litellm",
        examples=[{
            "model_provider": "openai/gpt-4",
            "model_provider_args": {
                "api_key": "sk-...", 
                "max_tokens": 500,
                "temperature": 0.0
            }
        }]
    )
    handlers: List[Dict[str, Any]] = Field(default_factory=list,alias="logging_handlers")
    json_output: bool = False
    sentence_transformer_model: str = Field(default="jinaai/jina-embeddings-v3", description="Name or path of the sentence transformer model")
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="URI of the Neo4j database")
    neo4j_username: str = Field(default="neo4j", description="Username for the Neo4j database")
    neo4j_password: str = Field(default="Ke7Rk7jB:Jn2Uz:", description="Password for the Neo4j database")