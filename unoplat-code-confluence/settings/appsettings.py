from typing import Optional
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    togetherai_api_key: Optional[str] = None
    github_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'