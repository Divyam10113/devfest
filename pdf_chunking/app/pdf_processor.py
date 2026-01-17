"""
PDF processing module using LlamaParse.
Handles PDF upload, parsing, and text extraction with support for images and tables.
"""
import os
import logging
from typing import Dict, List, Tuple
from llama_parse import LlamaParse
from app.config import get_settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDFs using LlamaParse for advanced parsing."""
    
    def __init__(self):
        """Initialize LlamaParse client."""
        settings = get_settings()
        self.parser = LlamaParse(
            api_key=settings.llama_cloud_api_key,
            result_type="markdown",  # Get markdown output
            verbose=True,
            language="en",
        )
    
    async def parse_pdf(self, file_path: str, filename: str) -> Dict[str, any]:
        """
        Parse PDF using LlamaParse.
        
        Args:
            file_path: Path to the PDF file
            filename: Original filename
            
        Returns:
            Dictionary containing parsed text, pages, and metadata
        """
        logger.info(f"Starting PDF parse for: {filename}")
        
        try:
            # Parse the PDF - LlamaParse handles the heavy lifting
            documents = self.parser.load_data(file_path)
            
            # LlamaParse returns a list of Document objects
            # Each document has .text (markdown) and .metadata
            
            parsed_pages = []
            full_text = ""
            
            for idx, doc in enumerate(documents):
                page_num = idx + 1
                page_text = doc.text
                
                parsed_pages.append({
                    "page": page_num,
                    "text": page_text,
                    "char_count": len(page_text)
                })
                
                full_text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
            
            logger.info(f"Successfully parsed {len(parsed_pages)} pages from {filename}")
            
            return {
                "filename": filename,
                "full_text": full_text.strip(),
                "pages": parsed_pages,
                "total_pages": len(parsed_pages),
                "total_chars": len(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error parsing PDF {filename}: {str(e)}")
            raise Exception(f"PDF parsing failed: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text from parsing
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace("\x00", "")
        
        # Normalize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        return text.strip()
    
    def extract_page_number(self, text: str) -> int:
        """
        Extract page number from text if present in LlamaParse output.
        
        Args:
            text: Text chunk
            
        Returns:
            Page number (default to 1 if not found)
        """
        # LlamaParse typically includes page markers
        # Format: "--- Page X ---"
        import re
        match = re.search(r'---\s*Page\s+(\d+)\s*---', text)
        if match:
            return int(match.group(1))
        return 1
