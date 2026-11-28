from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Document RAG Platform"
    app_env: str = "local"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    upload_dir: Path = Path("data/uploads")
    processed_dir: Path = Path("data/processed")
    vector_store_dir: Path = Path("vector_store")
    max_upload_size_mb: int = 10
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"
    app_api_key: str | None = None
    database_url: str = "sqlite:///./data/app.db"
    openai_api_key: str | None = None
    openai_api_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"
    aws_region: str | None = None
    aws_s3_bucket: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
