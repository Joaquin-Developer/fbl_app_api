import os
from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


env = os.getenv("ENV") or "development"
env_dir = os.getenv("ENV_DIR") or os.getcwd()


class Settings(BaseSettings):
    PROJECT_NAME: str = "fbl-app-api"
    DESCRIPTION: str = "FBL-APP Main API"
    ENVIRONMENT: str

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    DATABASE_DSN: str
    STATISTICS_SERVICE_URL: str = "http://127.0.0.1:8001"

    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings(_env_file=f"{env_dir}/environments/.env.{env}", ENVIRONMENT=env)
