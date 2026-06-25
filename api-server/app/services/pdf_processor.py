"""
PDF processing service - Extract text from PDF files
"""

import os
from pathlib import Path
from typing import List, Dict
import logging

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handle PDF text extraction"""
    
    def __init__(self):
        """Initialize PDF processor"""
        self.pdf_dir = Path(os.environ.get("PDF_DIR", "resources"))
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, str]]:
        """
        Extract text from PDF file, one page per document
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of documents with title, text, and metadata
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            reader = PdfReader(pdf_path)
            documents = []
            
            pages = reader.pages
            for page_num, page in enumerate(pages, start=1):
                try:
                    text = page.extract_text() or ""
                    
                    # Skip empty pages
                    if not text.strip():
                        logger.debug(f"Skipping empty page {page_num}")
                        continue
                    
                    # Get metadata
                    title = f"page_{page_num:04d}"
                    
                    documents.append({
                        "title": title,
                        "text": text,
                        "page_number": page_num,
                        "source": pdf_path
                    })
                    
                    logger.debug(f"Extracted page {page_num}")
                
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(documents)} pages from PDF")
            return documents
        
        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            return []
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return []
    
    def find_pdf(self, filename: str = "document.pdf") -> str:
        """
        Find PDF file in resources directory
        
        Args:
            filename: Name of the PDF to find
        
        Returns:
            Path to PDF file
        
        Raises:
            FileNotFoundError: If PDF not found
        """
        pdf_path = self.pdf_dir / filename
        
        if pdf_path.exists():
            return str(pdf_path)
        
        # Try to find any PDF in the directory
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if pdf_files:
            logger.warning(f"Requested PDF not found, using: {pdf_files[0]}")
            return str(pdf_files[0])
        
        raise FileNotFoundError(
            f"No PDF found in {self.pdf_dir}. "
            f"Please place {filename} in the resources directory."
        )
