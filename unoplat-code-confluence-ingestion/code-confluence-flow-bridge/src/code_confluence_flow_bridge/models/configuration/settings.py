# Standard Library
from enum import Enum
from typing import Any, Dict, List, Optional

# Third Party
from pydantic import AnyUrl, BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProgrammingLanguage(str, Enum):
    PYTHON = 'python'

class PackageManagerType(str, Enum):
    POETRY = "poetry"
    PIP = "pip"
class DatabaseType(str, Enum):
    NEO4J = "neo4j"

# Configuration Models (BaseModel for JSON config)
class ProgrammingLanguageMetadata(BaseModel):
    language: ProgrammingLanguage
    package_manager: PackageManagerType
    language_version: Optional[str] = None

class CodebaseConfig(BaseModel):
    codebase_folder_name: str
    root_package_name: Optional[str] = None
    programming_language_metadata: ProgrammingLanguageMetadata

class RepositorySettings(BaseModel):
    git_url: str
    output_path: str
    codebases: List[CodebaseConfig]
    
class LLMProviderConfig(BaseModel):
    llm_model_provider: str
    llm_model_provider_args: Dict[str, Any]




# Environment Settings (BaseSettings for environment variables)
class EnvironmentSettings(BaseSettings):
    """Environment variables and secrets"""
    model_config = SettingsConfigDict(
        env_prefix="UNOPLAT_",
        env_file=('.env.dev','.env.test','.env.prod'),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',  # Ignore extra fields
        populate_by_name=True,
        env_parse_none_str=None  # Changed from list to None to fix type error
    )

    
    neo4j_host : str = Field(
        default=...,
        alias="NEO4J_HOST"
    )
    
    neo4j_port : int = Field(
        default=...,
        alias="NEO4J_PORT"
    )
    
    neo4j_username: str = Field(
        default=...,
        alias="NEO4J_USERNAME"
    )
    neo4j_password: SecretStr = Field(
        default=...,
        alias="NEO4J_PASSWORD"
    )

    @property
    def neo4j_connection_params(self) -> dict:
        """Return validated Neo4j connection parameters"""
        return {
            "url": str(self.neo4j_url),
            "username": self.neo4j_username,
            "password": self.neo4j_password.get_secret_value()
        }



