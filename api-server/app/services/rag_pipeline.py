"""
RAG Pipeline - Orchestrate the entire retrieval-augmented generation workflow
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

from app.services.storage import StorageService
from app.services.pdf_processor import PDFProcessor
from app.services.vector_db import VectorDBService
from app.services.llm_service import LLMService
from app.models.database import db, RAGPipelineLog, Conversation
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrate RAG pipeline: PDF → Text → Embeddings → Vector DB → LLM Response"""
    
    def __init__(self):
        """Initialize RAG pipeline services"""
        self.storage = StorageService()
        self.pdf_processor = PDFProcessor()
        self.vector_db = VectorDBService()
        self.llm = LLMService()
        
        # Text splitting configuration
        self.chunk_size = int(os.environ.get("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", 200))
        self.k_results = int(os.environ.get("RAG_K_RESULTS", 4))

        # Maximum size (characters) of a single generated text file before it is
        # split into smaller text files
        self.text_file_max_chars = int(os.environ.get("TEXT_FILE_MAX_CHARS", 50000))

        # Supported upload extensions
        self.allowed_extensions = {".pdf", ".txt"}
    
    @staticmethod
    def _sanitize_base_name(filename: str) -> str:
        """Build a safe base name (no extension) for generated text files"""
        stem = Path(filename).stem
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("_")
        return safe or "document"

    def _split_text_into_segments(self, content: str) -> List[str]:
        """
        Split a large text document into smaller segments so each generated
        text file stays under ``text_file_max_chars``.

        Splitting happens on paragraph/line boundaries where possible.
        Returns a single-element list when the document is already small enough.
        """
        if len(content) <= self.text_file_max_chars:
            return [content]

        segments: List[str] = []
        current = ""

        # Prefer paragraph boundaries, fall back to lines, then hard splits
        paragraphs = re.split(r"(\n\s*\n)", content)

        def flush():
            nonlocal current
            if current.strip():
                segments.append(current)
            current = ""

        for piece in paragraphs:
            if not piece:
                continue

            # A single piece larger than the limit must be hard-split
            if len(piece) > self.text_file_max_chars:
                flush()
                for i in range(0, len(piece), self.text_file_max_chars):
                    segments.append(piece[i:i + self.text_file_max_chars])
                continue

            if len(current) + len(piece) > self.text_file_max_chars:
                flush()
            current += piece

        flush()
        return [seg for seg in segments if seg.strip()]

    def process_upload(self, file_path: str, original_filename: str) -> Dict[str, any]:
        """
        Process an uploaded document (``.pdf`` or ``.txt``):

        1. Convert a PDF into per-page text files, or split a large text file
           into smaller text files when necessary.
        2. Persist the original upload and generated text files to storage
           (separate storage container locally, S3 in AWS).
        3. Chunk the text, embed it, and add it to the vector database.

        Args:
            file_path: Local path to the uploaded file (used for extraction).
            original_filename: The original name of the uploaded file.

        Returns:
            Dictionary with processing results.
        """
        pipeline_log = RAGPipelineLog(
            status="running",
            started_at=datetime.utcnow()
        )
        db.session.add(pipeline_log)
        db.session.commit()

        try:
            ext = Path(original_filename).suffix.lower()
            if ext not in self.allowed_extensions:
                raise Exception(
                    f"Unsupported file type '{ext or 'unknown'}'. "
                    f"Only .pdf and .txt files are allowed."
                )

            base_name = self._sanitize_base_name(original_filename)
            logger.info(f"Processing uploaded {ext} document: {original_filename}")

            # Persist the original upload to storage (S3/MinIO or local)
            try:
                with open(file_path, "rb") as fh:
                    self.storage.save_upload(f"{base_name}{ext}", fh.read())
            except Exception as e:
                logger.warning(f"Failed to persist original upload: {e}")

            documents: List[Dict[str, any]] = []
            text_files_created: List[str] = []

            if ext == ".pdf":
                pages = self.pdf_processor.extract_text_from_pdf(file_path)
                if not pages:
                    raise Exception("No text could be extracted from the PDF")

                for page in pages:
                    page_num = page.get("page_number", 0)
                    text = page.get("text", "")
                    txt_name = f"{base_name}_page_{page_num:04d}.txt"
                    self.storage.save_text_file(txt_name, text)
                    text_files_created.append(txt_name)
                    documents.append({
                        "text": text,
                        "title": txt_name,
                        "page_number": page_num,
                        "source": original_filename
                    })

            else:  # .txt
                content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                if not content.strip():
                    raise Exception("The uploaded text file is empty")

                segments = self._split_text_into_segments(content)
                multiple = len(segments) > 1
                for idx, segment in enumerate(segments, start=1):
                    txt_name = (
                        f"{base_name}_part_{idx:04d}.txt" if multiple else f"{base_name}.txt"
                    )
                    self.storage.save_text_file(txt_name, segment)
                    text_files_created.append(txt_name)
                    documents.append({
                        "text": segment,
                        "title": txt_name,
                        "part_number": idx,
                        "source": original_filename
                    })

            logger.info(
                f"Created {len(text_files_created)} text file(s) from {original_filename}"
            )

            # Chunk text for embedding
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", " ", ""]
            )

            chunks: List[Dict[str, any]] = []
            for doc in documents:
                metadata = {k: v for k, v in doc.items() if k not in ("text", "title")}
                for chunk_idx, chunk_text in enumerate(splitter.split_text(doc["text"])):
                    chunks.append({
                        "text": chunk_text,
                        "title": f"{doc['title']}_chunk_{chunk_idx}",
                        "chunk_index": chunk_idx,
                        **metadata
                    })

            if not chunks:
                raise Exception("No text chunks were produced from the document")

            # Update (append to) the vector database and run embedding
            chunks_added = self.vector_db.add_documents(chunks)
            logger.info(f"Added {chunks_added} chunks to the vector database")

            pipeline_log.status = "completed"
            pipeline_log.chunks_created = chunks_added
            pipeline_log.completed_at = datetime.utcnow()
            db.session.commit()

            return {
                "status": "completed",
                "filename": original_filename,
                "file_type": ext.lstrip("."),
                "text_files_created": len(text_files_created),
                "chunks_created": chunks_added,
                "pages_processed": len(documents),
                "message": (
                    f"Processed {original_filename}: created {len(text_files_created)} "
                    f"text file(s) and added {chunks_added} chunks to the vector database."
                )
            }

        except Exception as e:
            logger.error(f"Failed to process uploaded document: {e}")
            pipeline_log.status = "failed"
            pipeline_log.error_message = str(e)
            pipeline_log.completed_at = datetime.utcnow()
            db.session.commit()

            return {
                "status": "failed",
                "filename": original_filename,
                "error": str(e),
                "message": f"Failed to process upload: {e}"
            }

    def ask_question(self, question: str) -> Dict[str, any]:
        """
        Ask a question and get an answer using RAG
        
        Args:
            question: User's question
        
        Returns:
            Dictionary with answer and sources
        """
        try:
            logger.info(f"Processing question: {question[:50]}...")
            
            # Step 1: Search vector database for relevant documents
            logger.debug("Searching vector database")
            search_results = self.vector_db.search(question, k=self.k_results)
            
            if not search_results:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I couldn't find relevant information about that topic in the knowledge base.",
                    "sources": [],
                    "error": "No relevant documents found"
                }
            
            # Step 2: Build context from search results
            logger.debug(f"Found {len(search_results)} relevant documents")
            context = "\n\n---\n\n".join([
                f"Source: {doc['metadata'].get('title', 'Unknown')}\n{doc['content']}"
                for doc in search_results
            ])
            
            # Step 3: Generate answer using LLM
            logger.debug("Generating answer with LLM")
            answer = self.llm.generate_answer(question, context)
            
            # Step 4: Extract sources
            sources = self.llm.extract_sources(search_results)
            
            # Step 5: Save conversation to database
            logger.debug("Saving conversation to database")
            conversation = Conversation(
                question=question,
                answer=answer,
                sources=sources
            )
            db.session.add(conversation)
            db.session.commit()
            
            logger.info(f"Successfully answered question")
            
            return {
                "answer": answer,
                "sources": sources,
                "conversation_id": str(conversation.id)
            }
        
        except Exception as e:
            logger.error(f"Failed to process question: {e}")
            return {
                "answer": "An error occurred while processing your question. Please try again.",
                "sources": [],
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, any]:
        """
        Get RAG pipeline status
        
        Returns:
            Dictionary with pipeline status
        """
        try:
            collection_info = self.vector_db.get_collection_info()
            
            # Get latest pipeline execution
            latest_log = RAGPipelineLog.query.order_by(
                RAGPipelineLog.started_at.desc()
            ).first()
            
            last_execution = None
            if latest_log:
                last_execution = {
                    "status": latest_log.status,
                    "chunks_created": latest_log.chunks_created,
                    "started_at": latest_log.started_at.isoformat(),
                    "completed_at": latest_log.completed_at.isoformat() if latest_log.completed_at else None
                }
            
            # Get conversation count
            conversation_count = Conversation.query.count()
            
            return {
                "vector_db": collection_info,
                "last_execution": last_execution,
                "conversation_count": conversation_count,
                "status": "ready"
            }
        
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Create singleton instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
