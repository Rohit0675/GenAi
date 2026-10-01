from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Agent API
    agent_host: str = Field(default="127.0.0.1", alias="AGENT_HOST")
    agent_port: int = Field(default=8000, alias="AGENT_PORT")

    # RAG API
    rag_base_url: str = Field(
        default="http://127.0.0.1:8001",
        alias="RAG_BASE_URL",
    )
    rag_timeout_seconds: float = Field(
        default=30.0,
        alias="RAG_TIMEOUT_SECONDS",
    )

    # LangGraph retrieval control
    max_retrieval_iterations: int = Field(
        default=2,
        alias="MAX_RETRIEVAL_ITERATIONS",
    )
    default_top_k: int = Field(
        default=8,
        alias="DEFAULT_TOP_K",
    )

    # LLM configuration
    llm_provider: str = Field(
        default="ollama",
        alias="LLM_PROVIDER",
    )
    llm_model: str = Field(
        default="",
        alias="LLM_MODEL",
    )
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        alias="OLLAMA_BASE_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()