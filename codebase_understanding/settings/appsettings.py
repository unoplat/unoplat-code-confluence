from typing import Optional
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    download_url: str
    download_directory: str
    github_token: Optional[str] = None  # Add GitHub token field

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'