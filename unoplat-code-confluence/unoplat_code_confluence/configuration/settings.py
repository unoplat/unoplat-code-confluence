# Standard Library
import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"

# Enums for type safety
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
    markdown_output_path: str
    codebases: List[CodebaseConfig]

class ArchGuardConfig(BaseModel):
    download_url: str
    download_directory: str

class LLMProviderConfig(BaseModel):
    llm_model_provider: str
    llm_model_provider_args: Dict[str, Any]

class DatabaseConfig(BaseModel):
    name: DatabaseType
    uri: str

class DatabaseSettings(BaseModel):
    host: str
    port: int

# Environment Settings (BaseSettings for environment variables)
class EnvironmentSettings(BaseSettings):
    """Environment variables and secrets"""
    model_config = SettingsConfigDict(
        env_prefix="UNOPLAT_",
        env_file='.env.dev',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',  # Ignore extra fields
        populate_by_name=True,
        env_parse_none_str=None  # Changed from list to None to fix type error
    )

    # Environment
    env: Environment = Field(default=Environment.DEV)
    debug: bool = Field(default=False)

    # Secrets - field names should match env vars without prefix
    github_token: str = Field(
        default=...,
        alias="GITHUB_TOKEN"
    )
    llm_api_key: Optional[str] = Field(
        default=None,
        alias="LLM_API_KEY"
    )
    neo4j_username: Optional[str] = Field(
        default=None,
        alias="NEO4J_USERNAME"
    )
    neo4j_password: Optional[str] = Field(
        default=None,
        alias="NEO4J_PASSWORD"
    )

    @classmethod
    def load(cls) -> "EnvironmentSettings":
        """Load environment settings from .env file and environment variables"""
        try:
            return cls()
        except ValidationError as e:
            env_vars = {
                key: value for key, value in os.environ.items() 
                if key.startswith("UNOPLAT_")
            }
            raise ValueError(
                f"Failed to load environment settings. \n"
                f"Current environment variables: {env_vars}\n"
                f"Validation errors: {str(e)}"
            )

# Main Configuration (BaseModel for JSON config)
class AppConfig(BaseModel):
    """JSON configuration"""
    repositories: List[RepositorySettings]
    archguard: ArchGuardConfig
    logging_handlers: List[Dict[str, Any]]
    llm_provider_config: Optional[LLMProviderConfig] = None
    databases: Optional[List[DatabaseConfig]] = None
    json_output: Optional[bool] = None
    sentence_transformer_model: Optional[str] = None

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """Load configuration from JSON file"""
        if config_path:
            config_file = config_path
        else:
            env = EnvironmentSettings.load().env
            config_file = f'config.{env}.json'

        with open(config_file, 'r') as f:
            config_data = json.loads(f.read())
        return cls(**config_data)

# Main Settings Class
class AppSettings:
    """Application settings combining environment variables and JSON config"""
    def __init__(self, config_path: Optional[str] = None):
        self._env_settings = EnvironmentSettings.load()
        self._config = AppConfig.load(config_path)

    @property
    def env(self) -> Environment:
        return self._env_settings.env

    @property
    def debug(self) -> bool:
        return self._env_settings.debug

    @property
    def secrets(self) -> EnvironmentSettings:
        return self._env_settings

    @property
    def config(self) -> AppConfig:
        return self._config

    # Convenience properties
    @property
    def repositories(self) -> List[RepositorySettings]:
        return self.config.repositories

    @property
    def databases(self) -> List[DatabaseConfig]:
        if self.config.databases is None:
            return []  # Return empty list instead of None
        return self.config.databases

    @classmethod
    def get_settings(cls, config_path: Optional[str] = None) -> "AppSettings":
        """
        Get application settings with optional config file override
        Args:
            config_path: Optional path to JSON config file
        """
        return cls(config_path)