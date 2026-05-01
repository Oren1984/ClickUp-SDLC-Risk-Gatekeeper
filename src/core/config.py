from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Typed application settings loaded from .env at startup.

    All values serve as startup defaults only. Runtime configuration
    (e.g. Streamlit sidebar selections) is passed as explicit arguments
    to pipeline components — settings are never re-read inside pipeline logic.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_env: str = "local"
    log_level: str = "INFO"

    # Mock mode — safe default, no API keys required
    mock_mode: bool = True

    # Embedding provider — options: mock | huggingface | openai | gemini
    embedding_provider: str = "mock"
    embedding_model: str = "mock-384"

    # Vector store — options: chroma | faiss
    vector_store: str = "chroma"

    # Chunking — options: recursive | fixed
    chunk_strategy: str = "recursive"
    chunk_size: int = 500
    chunk_overlap: int = 100

    # Retrieval
    top_k: int = 5

    # Re-ranking
    use_reranker: bool = False

    # Optional API keys — left empty to stay in mock mode
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Paths
    data_dir: str = "data"
    vector_db_dir: str = "vector_db"
    results_dir: str = "results"

    # Upload limits
    max_upload_mb: int = 10


# Module-level singleton — loaded once at import time.
settings = AppSettings()
