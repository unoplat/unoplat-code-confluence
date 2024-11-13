from enum import Enum
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationInfo, field_validator, Field
import re


class PackageManagerType(Enum):
    POETRY = "poetry"
    PIP = "pip"

    
#TODO: add pip support
class PackageManager(BaseModel):
    PYTHON: List[str] = Field(default_factory=lambda: ["poetry","pip"], frozen=True)
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
    language_version: str

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

class AppConfig(BaseModel):
    local_workspace_path: str
    output_path: str
    output_file_name: str
    codebase_name: str
    programming_language_metadata: ProgrammingLanguageMetadata
    repo: RepoConfig
    api_tokens: Dict[str, str]
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
    parallisation: int = 1
    json_output: bool = False
    sentence_transformer_model: str = Field(default="jinaai/jina-embeddings-v3", description="Name or path of the sentence transformer model")
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="URI of the Neo4j database")
    neo4j_username: str = Field(default="neo4j", description="Username for the Neo4j database")
    neo4j_password: str = Field(default="Ke7Rk7jB:Jn2Uz:", description="Password for the Neo4j database")
 
    @field_validator('api_tokens')
    @classmethod
    def check_api_tokens(cls, value: Dict[str, str], info: ValidationInfo) -> Dict[str, str]:
        if 'github_token' not in value:
            raise ValueError("github_token is required in api_tokens")
        if len(value) != 1:
            raise ValueError("api_tokens must only contain github_token")
        return value