import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Database
    database_host: str = os.environ.get("DB_HOST")
    database_port: int = os.environ.get("DB_PORT")
    database_name: str = os.environ.get("DB_NAME")
    database_user: str = os.environ.get("DB_USERNAME")
    database_password: str = os.environ.get("DB_PASSWORD")
    database_schema: str = os.environ.get("DB_SCHEMA")
    pool_size: int = os.environ.get("POOL_SIZE")
    max_overflow: int = os.environ.get("MAX_OVERFLOW")
    pool_recycle: int = os.environ.get("POOL_RECYCLE")
    pool_timeout: int = os.environ.get("POOL_TIMEOUT")

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
