"""
Ingestion & Knowledge Service

A microservice for PDF parsing, chunking, vectorization, and semantic search.
Part of the compliance RAG system.

Features:
- LlamaParse integration for advanced PDF parsing
- Parent-child chunking strategy
- Semantic caching (73% cost reduction)
- ChromaDB vector storage
- Automatic PDF pre-loading
"""

__version__ = "1.0.0"
__author__ = "DevFest Team"
__service__ = "Ingestion & Knowledge Service"

# Convenient imports for external use
from app.config import get_settings
from app.models import (
    UploadResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    HealthCheck,
    CollectionInfo
)

__all__ = [
    "get_settings",
    "UploadResponse",
    "SearchRequest",
    "SearchResponse",
    "SearchResultItem",
    "HealthCheck",
    "CollectionInfo",
]
