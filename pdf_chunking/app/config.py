"""
Configuration module for the Ingestion & Knowledge Service.
Loads environment variables and provides centralized config access.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    llama_cloud_api_key: str
    google_api_key: str  # Google Gemini API (FREE embeddings!)
    
    # ChromaDB Configuration
    chroma_db_path: str = "./chroma_db"  # Local directory
    chroma_collection_name: str = "compliance_docs"
    
    # Chunking Configuration
    parent_chunk_size: int = 1200
    child_chunk_size: int = 300
    chunk_overlap: int = 100
    
    # File Upload Limits
    max_file_size_mb: int = 50
    
    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Google Embedding Configuration (FREE API)
    embedding_model: str = "models/text-embedding-004"  # Google's latest, 768 dimensions
    embedding_dimensions: int = 768
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow ChromaDB and other env vars we don't use directly


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
