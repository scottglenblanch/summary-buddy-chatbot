"""
PDF processing service - Extract text from PDF files
"""

from typing import List, Dict
import logging

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handle PDF text extraction"""

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
