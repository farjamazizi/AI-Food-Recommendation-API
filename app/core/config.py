from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Food Recommendation System"
    app_version: str = "1.0.0"
    environment: str = "production"

    data_path: Path = Field(default=Path("data/FoodDataSet.json"))
    chroma_path: Path = Field(default=Path(".chroma"))
    chroma_collection: str = "foods"

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout_seconds: float = 90.0

    default_results: int = 5
    max_results: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FOOD_API_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
