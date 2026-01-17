"""
FastAPI application for the Ingestion & Knowledge Service.
Main entry point for the microservice.
"""
import logging
import os
import tempfile
import nest_asyncio
from contextlib import asynccontextmanager

# Apply nested asyncio patch for LlamaParse
nest_asyncio.apply()
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.config import get_settings
from app.models import (
    UploadResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    HealthCheck,
    CollectionInfo
)
from app.pdf_processor import PDFProcessor
from app.chunker import Chunker
from app.vectorizer import Vectorizer
from app.vector_store import VectorStore
from app.semantic_cache import SemanticCache
from app.preloader import PDFPreloader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances (initialized at startup)
pdf_processor = None
chunker = None
vectorizer = None
vector_store = None
semantic_cache = None
preload_stats = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    global pdf_processor, chunker, vectorizer, vector_store, semantic_cache, preload_stats
    
    # Initialize service components
    
    pdf_processor = PDFProcessor()
    chunker = Chunker()
    vectorizer = Vectorizer()
    vector_store = VectorStore()
    
    # Initialize semantic cache (reduces API costs by ~73%)
    semantic_cache = SemanticCache(similarity_threshold=0.95)
    
    # Pre-load default PDFs
    preloader = PDFPreloader(
        pdf_processor=pdf_processor,
        chunker=chunker,
        vectorizer=vectorizer,
        vector_store=vector_store,
        preload_dir="./data/pdfs"
    )
    
    preload_stats = await preloader.preload_pdfs()
    if preload_stats.get('processed', 0) > 0:
        logger.info(f"Loaded {preload_stats['processed']} PDF(s)")
    
    logger.info("Service ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down service...")


# Create FastAPI app
app = FastAPI(
    title="Ingestion & Knowledge Service",
    description="PDF processing, chunking, and vector storage for RAG system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck()


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """
    Upload and process a PDF document.
    
    Steps:
    1. Parse PDF with LlamaParse
    2. Create parent-child chunks
    3. Generate embeddings
    4. Store in ChromaDB
    """
    settings = get_settings()
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {settings.max_file_size_mb}MB limit"
        )
    
    logger.info(f"Processing upload: {file.filename} ({file_size / 1024:.2f} KB)")
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            temp_file = tmp.name
            content = await file.read()
            tmp.write(content)
        
        # Step 1: Parse PDF
        logger.info("Step 1: Parsing PDF with LlamaParse...")
        parsed_data = await pdf_processor.parse_pdf(temp_file, file.filename)
        
        # Step 2: Create chunks
        logger.info("Step 2: Creating parent-child chunks...")
        parent_chunks, child_chunks = chunker.chunk_text(
            text=parsed_data["full_text"],
            filename=file.filename,
            pages=parsed_data["pages"]
        )
        
        # Step 3: Generate embeddings (only for child chunks)
        logger.info("Step 3: Generating embeddings...")
        child_texts = [chunk["text"] for chunk in child_chunks]
        embeddings = vectorizer.create_embeddings(child_texts)
        
        # Step 4: Store in ChromaDB
        logger.info("Step 4: Storing in ChromaDB...")
        num_stored = vector_store.add_chunks(child_chunks, embeddings)
        
        logger.info(f"Successfully processed {file.filename}")
        
        return UploadResponse(
            document_id=f"doc_{file.filename.replace('.pdf', '')}",
            filename=file.filename,
            num_parent_chunks=len(parent_chunks),
            num_child_chunks=len(child_chunks),
            status="success",
            message=f"Processed {parsed_data['total_pages']} pages"
        )
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for relevant chunks using vector similarity.
    
    This endpoint is called by the RAG Intelligence Service (Service 4).
    Uses semantic caching to reduce embedding API costs by ~73%.
    """
    logger.info(f"Search request: '{request.query}' (top_k={request.top_k})")
    
    try:
        # Step 1: Create query embedding with semantic caching
        query_embedding, was_cached = semantic_cache.get_or_create_embedding(
            query=request.query,
            embedding_function=vectorizer.create_query_embedding
        )
        
        if was_cached:
            logger.info("💰 Saved API cost with cache hit!")
        
        # Step 2: Search ChromaDB
        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            filters=request.filters
        )
        
        # Step 3: Format results
        formatted_results = []
        for result in results:
            metadata = result["metadata"]
            
            item = SearchResultItem(
                text=result["text"],
                score=result["score"],
                page=metadata.get("page", 1),
                source=metadata.get("source", "unknown"),
                parent_text=metadata.get("parent_text") if request.include_parent else None,
                metadata=metadata
            )
            formatted_results.append(item)
        
        logger.info(f"Returning {len(formatted_results)} results")
        
        return SearchResponse(
            results=formatted_results,
            query=request.query,
            num_results=len(formatted_results)
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/collections", response_model=CollectionInfo)
async def get_collection_info():
    """Get information about stored collections."""
    try:
        stats = vector_store.get_collection_stats()
        
        return CollectionInfo(
            collection_name=stats["collection_name"],
            num_documents=stats["num_documents"],
            num_chunks=stats["num_chunks"]
        )
        
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get info: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get service statistics including cache performance."""
    try:
        cache_stats = semantic_cache.get_stats()
        collection_stats = vector_store.get_collection_stats()
        
        return {
            "service": "Ingestion & Knowledge Service",
            "cache": cache_stats,
            "collections": collection_stats,
            "preload": preload_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
