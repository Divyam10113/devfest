"""
Text chunking module implementing parent-child chunking strategy.
"""
import logging
import tiktoken
from typing import List, Dict, Tuple
from app.config import get_settings

logger = logging.getLogger(__name__)


class Chunker:
    """Implements parent-child chunking strategy."""
    
    def __init__(self):
        """Initialize chunker with tiktoken encoder."""
        settings = get_settings()
        self.parent_size = settings.parent_chunk_size
        self.child_size = settings.child_chunk_size
        self.overlap = settings.chunk_overlap
        
        # Use tiktoken for accurate token counting (same as OpenAI)
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoder.encode(text))
    
    def chunk_text(
        self,
        text: str,
        filename: str,
        pages: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Create parent and child chunks from text.
        
        Args:
            text: Full document text
            filename: Source filename
            pages: Page information from PDF processor
            
        Returns:
            Tuple of (parent_chunks, child_chunks)
        """
        logger.info(f"Creating chunks for {filename}")
        
        # First, create parent chunks
        parent_chunks = self._create_chunks(
            text,
            chunk_size=self.parent_size,
            overlap=self.overlap
        )
        
        # Then, create child chunks from each parent
        all_child_chunks = []
        
        for parent_idx, parent_chunk in enumerate(parent_chunks):
            parent_id = f"{filename}_parent_{parent_idx}"
            
            # Create child chunks from this parent
            child_chunks = self._create_chunks(
                parent_chunk["text"],
                chunk_size=self.child_size,
                overlap=self.overlap // 2  # Smaller overlap for children
            )
            
            # Link children to parent
            for child_idx, child_chunk in enumerate(child_chunks):
                child_id = f"{parent_id}_child_{child_idx}"
                
                all_child_chunks.append({
                    "id": child_id,
                    "text": child_chunk["text"],
                    "parent_id": parent_id,
                    "parent_text": parent_chunk["text"],
                    "source": filename,
                    "page": self._estimate_page(child_chunk["start_pos"], text, pages),
                    "token_count": child_chunk["token_count"]
                })
            
            # Update parent metadata
            parent_chunk.update({
                "id": parent_id,
                "source": filename,
                "page": self._estimate_page(parent_chunk["start_pos"], text, pages),
                "num_children": len(child_chunks)
            })
        
        logger.info(
            f"Created {len(parent_chunks)} parent chunks and "
            f"{len(all_child_chunks)} child chunks for {filename}"
        )
        
        return parent_chunks, all_child_chunks
    
    def _create_chunks(
        self,
        text: str,
        chunk_size: int,
        overlap: int
    ) -> List[Dict]:
        """
        Create fixed-size chunks with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens
            overlap: Overlap in tokens
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        tokens = self.encoder.encode(text)
        
        start = 0
        chunk_idx = 0
        
        while start < len(tokens):
            # Get chunk tokens
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.encoder.decode(chunk_tokens)
            
            chunks.append({
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "start_pos": start,
                "end_pos": end,
                "chunk_index": chunk_idx
            })
            
            # Move to next chunk with overlap
            start += chunk_size - overlap
            chunk_idx += 1
        
        return chunks
    
    def _estimate_page(
        self,
        char_position: int,
        full_text: str,
        pages: List[Dict]
    ) -> int:
        """
        Estimate which page a character position belongs to.
        
        Args:
            char_position: Character position in full text
            full_text: Complete document text
            pages: Page information
            
        Returns:
            Estimated page number
        """
        if not pages:
            return 1
        
        # Simple heuristic: divide position by average chars per page
        avg_chars_per_page = len(full_text) / len(pages)
        estimated_page = int(char_position / avg_chars_per_page) + 1
        
        return min(estimated_page, len(pages))
