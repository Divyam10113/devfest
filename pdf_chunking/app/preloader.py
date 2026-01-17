"""
PDF preloader - loads default PDFs at startup.
"""
import logging
import os
from pathlib import Path
from typing import List
import asyncio

from app.pdf_processor import PDFProcessor
from app.chunker import Chunker
from app.vectorizer import Vectorizer
from app.vector_store import VectorStore

logger = logging.getLogger(__name__)


class PDFPreloader:
    """Pre-load PDFs from a directory at startup."""
    
    def __init__(
        self,
        pdf_processor: PDFProcessor,
        chunker: Chunker,
        vectorizer: Vectorizer,
        vector_store: VectorStore,
        preload_dir: str = "./data/pdfs"
    ):
        """
        Initialize preloader.
        
        Args:
            pdf_processor: PDF processor instance
            chunker: Chunker instance
            vectorizer: Vectorizer instance
            vector_store: Vector store instance
            preload_dir: Directory containing PDFs to pre-load
        """
        self.pdf_processor = pdf_processor
        self.chunker = chunker
        self.vectorizer = vectorizer
        self.vector_store = vector_store
        self.preload_dir = Path(preload_dir)
    
    async def preload_pdfs(self) -> dict:
        """
        Pre-load all PDFs from the preload directory.
        
        Returns:
            Dictionary with preload statistics
        """
        logger.info(f"Starting PDF pre-load from: {self.preload_dir}")
        
        # Create directory if it doesn't exist
        self.preload_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all PDFs
        pdf_files = list(self.preload_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDFs found in {self.preload_dir}")
            return {
                "status": "no_files",
                "message": f"No PDFs found in {self.preload_dir}. Place PDFs there for auto-loading."
            }
        
        logger.info(f"Found {len(pdf_files)} PDF(s) to pre-load")
        
        stats = {
            "total_files": len(pdf_files),
            "processed": 0,
            "failed": 0,
            "total_chunks": 0,
            "files": []
        }
        
        # Process each PDF
        for pdf_path in pdf_files:
            try:
                logger.info(f"Processing: {pdf_path.name}")
                
                # Check if already processed
                existing_stats = self.vector_store.get_collection_stats()
                if pdf_path.name in existing_stats.get("sources", []):
                    logger.info(f"⏭️  Skipping {pdf_path.name} - already in database")
                    stats["files"].append({
                        "filename": pdf_path.name,
                        "status": "skipped",
                        "reason": "already_loaded"
                    })
                    continue
                
                # Step 1: Parse PDF
                parsed_data = await self.pdf_processor.parse_pdf(
                    str(pdf_path),
                    pdf_path.name
                )
                
                # Step 2: Create chunks
                parent_chunks, child_chunks = self.chunker.chunk_text(
                    text=parsed_data["full_text"],
                    filename=pdf_path.name,
                    pages=parsed_data["pages"]
                )
                
                # Step 3: Generate embeddings
                child_texts = [chunk["text"] for chunk in child_chunks]
                embeddings = self.vectorizer.create_embeddings(child_texts)
                
                # Step 4: Store in ChromaDB
                num_stored = self.vector_store.add_chunks(child_chunks, embeddings)
                
                stats["processed"] += 1
                stats["total_chunks"] += num_stored
                stats["files"].append({
                    "filename": pdf_path.name,
                    "status": "success",
                    "chunks": num_stored,
                    "pages": parsed_data["total_pages"]
                })
                
                logger.info(f"✅ Loaded {pdf_path.name}: {num_stored} chunks from {parsed_data['total_pages']} pages")
                
            except Exception as e:
                logger.error(f"❌ Failed to process {pdf_path.name}: {e}")
                stats["failed"] += 1
                stats["files"].append({
                    "filename": pdf_path.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        logger.info(
            f"Pre-load complete: {stats['processed']} processed, "
            f"{stats['failed']} failed, {stats['total_chunks']} total chunks"
        )
        
        return stats
