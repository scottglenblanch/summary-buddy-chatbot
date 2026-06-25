"""
LLM service - Handle OpenAI API interactions
"""

import os
from typing import List, Dict, Optional
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMService:
    """Manage OpenAI API interactions"""
    
    def __init__(self):
        """Initialize LLM service"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Using cheaper mini model
        self.temperature = 0.3  # Lower temperature for consistent answers
    
    def generate_answer(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate answer using OpenAI API with context
        
        Args:
            question: User's question
            context: Retrieved context from vector database
            system_prompt: Custom system prompt (optional)
        
        Returns:
            Generated answer
        """
        try:
            if system_prompt is None:
                system_prompt = (
                    "You are a helpful Game Master for a role-playing game. "
                    "Answer questions based on the provided context from the knowledge base. "
                    "If the context doesn't contain the answer, say so. "
                    "Be concise and maintain the tone of a fantasy game master."
                )
            
            # Build the user message with context
            user_message = f"""Context from the knowledge base:
{context}

Question: {question}

Please provide a helpful answer based on the context above."""
            
            logger.debug(f"Generating answer for question: {question[:50]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.debug(f"Generated answer (tokens: {response.usage.total_tokens})")
            
            return answer
        
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise
    
    def extract_sources(self, documents: List[Dict[str, str]]) -> List[str]:
        """
        Extract source references from documents
        
        Args:
            documents: List of documents with metadata
        
        Returns:
            List of source references
        """
        sources = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            
            # Extract relevant metadata for source
            source_ref = metadata.get("title", "Unknown")
            if "page_number" in metadata:
                source_ref += f" (page {metadata['page_number']})"
            
            sources.append(source_ref)
        
        return sources
