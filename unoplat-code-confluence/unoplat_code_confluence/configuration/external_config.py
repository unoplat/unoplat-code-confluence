from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, ValidationInfo, field_validator


class LLMProvider(Enum):
    OPENAI = 'openai'
    COHERE = 'cohere'
    ANYSCALE = 'anyscale'
    TOGETHER = 'together'


    

class ProgrammingLanguage(Enum):
    # PYTHON = 'Python'
    JAVA = 'java'
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
    programming_language: str
    repo: RepoConfig
    api_tokens: Dict[str, str]
    llm_provider_config: Dict[str, Any]
 
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
    
    @field_validator('llm_provider_config')
    def check_llm_provider_config(cls, value, info:ValidationInfo):
        #TODO if key is in LLmProvider enum
        if not all(key in LLMProvider for key in value.keys()):
            raise ValueError("llm_provider_config keys must be in LLMProvider enum")
        return value
