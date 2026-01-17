"""
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class UploadResponse(BaseModel):
    """Response model for PDF upload."""
    document_id: str = Field(..., description="Unique identifier for the uploaded document")
    filename: str = Field(..., description="Original filename")
    num_parent_chunks: int = Field(..., description="Number of parent chunks created")
    num_child_chunks: int = Field(..., description="Number of child chunks created")
    status: str = Field(default="success", description="Processing status")
    message: Optional[str] = Field(None, description="Additional message")


class SearchRequest(BaseModel):
    """Request model for vector search."""
    query: str = Field(..., description="Natural language query")
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=20)
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    include_parent: bool = Field(default=True, description="Include parent chunk context")


class SearchResultItem(BaseModel):
    """Individual search result."""
    text: str = Field(..., description="Child chunk text")
    score: float = Field(..., description="Similarity score")
    page: int = Field(..., description="Page number from source PDF")
    source: str = Field(..., description="Source document filename")
    parent_text: Optional[str] = Field(None, description="Parent chunk context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """Response model for vector search."""
    results: List[SearchResultItem] = Field(..., description="Search results")
    query: str = Field(..., description="Original query")
    num_results: int = Field(..., description="Number of results returned")


class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy")
    service: str = Field(default="Ingestion & Knowledge Service")
    version: str = Field(default="1.0.0")


class CollectionInfo(BaseModel):
    """Collection information."""
    collection_name: str
    num_documents: int
    num_chunks: int
