"""
Configuration management for the RAG application.
Loads environment variables and provides centralized configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Embedding Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dimension: int = 1536  # text-embedding-3-small dimension

    # Vector Store Configuration
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./storage/faiss_index")

    # Chunking Strategy
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Retrieval Configuration
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "3"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/rag_app.log")

    # Application Configuration
    streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    class Config:
        case_sensitive = False

    def validate_config(self) -> bool:
        """Validate that required settings are properly configured."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        return True

    def get_paths(self):
        """Create necessary directories if they don't exist."""
        Path(self.vector_store_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
