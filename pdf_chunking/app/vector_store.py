"""
ChromaDB vector store module for storing and retrieving embeddings.
"""
import logging
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from app.config import get_settings

logger = logging.getLogger(__name__)

# Suppress ChromaDB telemetry errors (internal PostHog bug)
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)


class VectorStore:
    """Manage ChromaDB vector storage and retrieval."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        settings = get_settings()
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection_name = settings.chroma_collection_name
        self.collection = None
        
        # ChromaDB initialized successfully
    
    def get_or_create_collection(self):
        """Get or create the main collection."""
        if self.collection is None:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Compliance documents child chunks"}
            )
        return self.collection
    
    def add_chunks(
        self,
        chunks: List[Dict],
        embeddings: List[List[float]]
    ) -> int:
        """
        Add chunks and their embeddings to the vector store.
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            
        Returns:
            Number of chunks added
        """
        collection = self.get_or_create_collection()
        
        # Prepare data for ChromaDB
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "parent_id": chunk["parent_id"],
                "parent_text": chunk["parent_text"],
                "source": chunk["source"],
                "page": chunk["page"],
                "token_count": chunk["token_count"]
            }
            for chunk in chunks
        ]
        
        
        try:
            # Add to collection
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error adding chunks to ChromaDB: {str(e)}")
            raise Exception(f"Vector store insertion failed: {str(e)}")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of search results with metadata
        """
        collection = self.get_or_create_collection()
        
        
        try:
            # Build where clause for filters
            where_clause = None
            if filters:
                where_clause = filters
            
            # Query ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            
            if results and results["ids"] and len(results["ids"][0]) > 0:
                for idx in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][idx],
                        "text": results["documents"][0][idx],
                        "score": 1 - results["distances"][0][idx],  # Convert distance to similarity
                        "metadata": results["metadatas"][0][idx]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {str(e)}")
            raise Exception(f"Vector search failed: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        collection = self.get_or_create_collection()
        
        count = collection.count()
        
        # Get unique sources
        all_items = collection.get(include=["metadatas"])
        sources = set()
        if all_items and all_items["metadatas"]:
            sources = {meta.get("source", "unknown") for meta in all_items["metadatas"]}
        
        return {
            "collection_name": self.collection_name,
            "num_chunks": count,
            "num_documents": len(sources),
            "sources": list(sources)
        }
    
    def delete_by_source(self, source: str) -> int:
        """
        Delete all chunks from a specific source document.
        
        Args:
            source: Source filename
            
        Returns:
            Number of chunks deleted
        """
        collection = self.get_or_create_collection()
        
        logger.info(f"Deleting chunks from source: {source}")
        
        try:
            # Get all IDs for this source
            results = collection.get(
                where={"source": source},
                include=[]
            )
            
            if results and results["ids"]:
                collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} chunks")
                return len(results["ids"])
            
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting chunks: {str(e)}")
            raise Exception(f"Deletion failed: {str(e)}")
