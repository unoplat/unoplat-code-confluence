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
    UV = "uv"
class DatabaseType(str, Enum):
    NEO4J = "neo4j"

# Configuration Models (BaseModel for JSON config)
class ProgrammingLanguageMetadata(BaseModel):
    language: ProgrammingLanguage
    package_manager: PackageManagerType
    language_version: Optional[str] = None

class CodebaseConfig(BaseModel):
    codebase_folder: str
    root_package: Optional[str] = None
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
    
    neo4j_max_connection_lifetime: int = Field(
        default=3600,
        alias="NEO4J_MAX_CONNECTION_LIFETIME",
        description="The maximum lifetime of a connection to the Neo4j database in seconds"
    )
    
    neo4j_max_connection_pool_size: int = Field(
        default=50,
        alias="NEO4J_MAX_CONNECTION_POOL_SIZE",
        description="The maximum number of connections in the Neo4j connection pool"
    )
    
    neo4j_connection_acquisition_timeout: int = Field(
        default=60,
        alias="NEO4J_CONNECTION_ACQUISITION_TIMEOUT",
        description="The maximum time to wait for a connection to be acquired from the Neo4j connection pool in seconds"
    )



