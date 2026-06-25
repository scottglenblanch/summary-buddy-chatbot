"""
Vector database service - Manage PostgreSQL + pgvector vector store
"""

import os
from typing import List, Dict
import logging

from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class VectorDBService:
    """Manage PostgreSQL + pgvector vector database"""
    
    def __init__(self):
        """Initialize vector database service"""
        self.collection_name = os.environ.get("PGVECTOR_COLLECTION_NAME", "summary_buddy")
        self.connection_string = self._build_connection_string()
        
        # Initialize embeddings
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-large"
        )
        
        self.vector_db = None
    
    @staticmethod
    def _build_connection_string() -> str:
        """Build a SQLAlchemy connection string for pgvector"""
        return os.environ.get(
            "PGVECTOR_URL",
            os.environ.get(
                "DATABASE_URL",
                "postgresql://postgres:postgres@postgres:5432/summary_buddy_chatbot"
            )
        )
    
    def _get_vector_db(self) -> PGVector:
        """Get or create vector database instance"""
        if self.vector_db is None:
            self.vector_db = PGVector(
                connection_string=self.connection_string,
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
                use_jsonb=True,
            )
            logger.info(f"Connected to pgvector collection '{self.collection_name}'")
        
        return self.vector_db
    
    def add_documents(self, documents: List[Dict[str, str]]) -> int:
        """
        Add documents to vector database
        
        Args:
            documents: List of documents with 'text' and optional metadata
        
        Returns:
            Number of documents added
        """
        try:
            logger.info(f"Adding {len(documents)} documents to vector database")
            
            # Convert to LangChain documents
            docs = []
            for doc in documents:
                content = doc.get("text", "")
                metadata = {k: v for k, v in doc.items() if k != "text"}
                docs.append(Document(page_content=content, metadata=metadata))
            
            db = self._get_vector_db()
            db.add_documents(docs)
            
            logger.info(f"Successfully added {len(documents)} documents")
            return len(documents)
        
        except Exception as e:
            logger.error(f"Failed to add documents to vector database: {e}")
            raise
    
    def search(self, query: str, k: int = 4) -> List[Dict[str, str]]:
        """
        Search vector database for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of similar documents with relevance scores
        """
        try:
            db = self._get_vector_db()
            if db is None:
                logger.warning("Vector database not initialized")
                return []
            
            results = db.similarity_search_with_score(query, k=k)
            
            documents = []
            for doc, score in results:
                documents.append({
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                })
            
            logger.debug(f"Found {len(documents)} similar documents for query")
            return documents
        
        except Exception as e:
            logger.error(f"Failed to search vector database: {e}")
            return []
    
    def clear(self) -> bool:
        """
        Clear vector database
        
        Returns:
            True if successful
        """
        try:
            logger.info("Clearing vector database")
            
            db = self._get_vector_db()
            db.delete_collection()
            self.vector_db = None
            
            logger.info("Vector database cleared")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear vector database: {e}")
            return False
    
    def get_collection_info(self) -> Dict:
        """
        Get information about the vector database collection
        
        Returns:
            Collection metadata
        """
        try:
            engine = create_engine(self.connection_string)
            try:
                with engine.connect() as conn:
                    count = conn.execute(
                        text(
                            "SELECT COUNT(*) FROM langchain_pg_embedding e "
                            "JOIN langchain_pg_collection c ON e.collection_id = c.uuid "
                            "WHERE c.name = :name"
                        ),
                        {"name": self.collection_name},
                    ).scalar() or 0
            finally:
                engine.dispose()
            
            return {
                "status": "initialized",
                "document_count": count,
                "collection_name": self.collection_name,
                "backend": "postgresql+pgvector"
            }
        
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {
                "status": "not initialized",
                "collection_name": self.collection_name,
                "backend": "postgresql+pgvector"
            }
