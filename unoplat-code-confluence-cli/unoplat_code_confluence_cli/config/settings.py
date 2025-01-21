# Standard Library
import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional

# Third Party
from pydantic import BaseModel


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
    codebase_folder: str
    root_package: Optional[str] = None
    programming_language_metadata: ProgrammingLanguageMetadata

class RepositorySettings(BaseModel):
    git_url: str
    output_path: str
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


# Main Configuration (BaseModel for JSON config)
class AppConfig(BaseModel):
    """JSON configuration"""
    repositories: List[RepositorySettings]
    llm_provider_config: Optional[LLMProviderConfig] = None
    databases: Optional[List[DatabaseConfig]] = None
    json_output: Optional[bool] = None
    sentence_transformer_model: Optional[str] = None

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """Load configuration from JSON file"""
        if config_path:
            config_file = config_path
        with open(config_file, 'r') as f:
            config_data = json.loads(f.read())
        return cls(**config_data)

# Main Settings Class
class AppSettings:
    """Application settings combining environment variables and JSON config"""
    def __init__(self, config_path: Optional[str] = None):
        self._config = AppConfig.load(config_path)

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