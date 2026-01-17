"""
Vectorization module using Google's FREE Gemini API.
Zero cost embeddings with generous free tier!
"""
import logging
from typing import List
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)


class Vectorizer:
    """Create embeddings using Google's FREE Gemini API."""
    
    def __init__(self):
        """Initialize Google Gemini API client."""
        settings = get_settings()
        
        # Configure Google API
        genai.configure(api_key=settings.google_api_key)
        
        self.model_name = settings.embedding_model
        
        logger.info(f"✅ Google Embeddings configured: {self.model_name}")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts using Google's API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            
            # Google API processes texts individually or in small batches
            # For efficiency, we'll batch in groups of 100
            batch_size = 100
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Embed each text in the batch
                for text in batch:
                    result = genai.embed_content(
                        model=self.model_name,
                        content=text,
                        task_type="retrieval_document"  # Optimized for retrieval
                    )
                    embeddings.append(result['embedding'])
                
                logger.debug(f"Processed batch {i//batch_size + 1}")
            
            logger.info(f"✅ Created {len(embeddings)} embeddings (cost: $0.00)")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise Exception(f"Embedding creation failed: {str(e)}")
    
    def create_query_embedding(self, query: str) -> List[float]:
        """
        Create embedding for a single query.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"  # Optimized for queries
            )
            
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Error creating query embedding: {str(e)}")
            raise Exception(f"Query embedding failed: {str(e)}")
