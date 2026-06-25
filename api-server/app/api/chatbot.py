"""
Chatbot endpoints - Ask questions to the Game Master
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError
import logging

from app.services.rag_pipeline import get_rag_pipeline

logger = logging.getLogger(__name__)
chatbot_bp = Blueprint("chatbot", __name__)


class AskQuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Who is Kaladin?"
            }
        }


@chatbot_bp.route("/ask-game-master-chatbot", methods=["POST"])
def ask_game_master():
    """
    Ask the Game Master a question powered by RAG
    
    Expected JSON body:
    {
        "question": "Your question here"
    }
    
    Returns:
    {
        "answer": "Response from the Game Master",
        "sources": ["source1", "source2"],
        "conversation_id": "uuid"
    }
    """
    try:
        request_obj = AskQuestionRequest.model_validate(request.get_json(silent=True) or {})
        logger.info(f"Processing question: {request_obj.question[:50]}...")

        # Get RAG pipeline and ask question
        pipeline = get_rag_pipeline()
        response = pipeline.ask_question(request_obj.question)

        # Check if there was an error
        if "error" in response and response["error"]:
            logger.warning(f"RAG pipeline error: {response['error']}")
            return jsonify(response), 400

        logger.info("Successfully answered question")
        return jsonify(response), 200

    except ValidationError as e:
        logger.exception("Request validation error")
        return jsonify({"error": "Invalid request", "details": e.errors()}), 400
    except Exception as e:
        logger.exception("Unexpected error in ask_game_master")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
