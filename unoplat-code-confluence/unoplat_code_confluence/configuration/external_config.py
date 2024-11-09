from enum import Enum
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationInfo, field_validator, Field





    

class PythonPackageManager(str, Enum):
    POETRY = "poetry"
    PIP = "pip"

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

class AppConfig(BaseModel):
    local_workspace_path: str
    output_path: str
    output_file_name: str
    codebase_name: str
    programming_language_metadata: Dict[str, str] = Field(
        description="Metadata about the programming language and its package manager",
        example={
            "language": "python",
            "package_manager": "pip"
        }
    )
    repo: RepoConfig
    api_tokens: Dict[str, str]
    llm_provider_config: Dict[str, Any] = Field(
        description="Configuration for the LLM provider based on litellm",
        example={
            "model_provider": "openai/gpt-4",
            "model_provider_args": {
                "api_key": "sk-...",
                "max_tokens": 500,
                "temperature": 0.0
            }
        }
    )
    handlers: List[Dict[str, Any]] = Field(default_factory=list,alias="logging_handlers")
    parallisation: int = 1
    json_output: bool = False
    sentence_transformer_model: str = Field(default="jinaai/jina-embeddings-v3", description="Name or path of the sentence transformer model")
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="URI of the Neo4j database")
    neo4j_username: str = Field(default="neo4j", description="Username for the Neo4j database")
    neo4j_password: str = Field(default="Ke7Rk7jB:Jn2Uz:", description="Password for the Neo4j database")
 
    @field_validator('programming_language')
    def check_programming_language(cls, value, info:ValidationInfo):
        if value not in [member.value for member in ProgrammingLanguage]:
            raise ValueError("programming_language must be a valid programming language")
        return value


    @field_validator('api_tokens')
    def check_api_tokens(cls, value, info:ValidationInfo):
        if 'github_token' not in value:
            raise ValueError("github_token is required in api_tokens")
        if len(value) != 1:
            raise ValueError("api_tokens must only contain github_token")
        return value
   
    @field_validator('programming_language_metadata')
    def check_programming_language_metadata(cls, value, info: ValidationInfo):
        if 'language' not in value:
            raise ValueError("programming_language_metadata must contain 'language' key")
        
        if value['language'] not in [member.value for member in ProgrammingLanguage]:
            raise ValueError("programming_language_metadata['language'] must be a valid programming language")
        
        # Package manager validation based on language
        if value['language'] == 'python':
            if 'package_manager' not in value:
                raise ValueError("package_manager is required for Python projects")
            
            if value['package_manager'] not in [member.value for member in PythonPackageManager]:
                raise ValueError("For Python projects, package_manager must be either 'poetry' or 'pip'")
        
        return value