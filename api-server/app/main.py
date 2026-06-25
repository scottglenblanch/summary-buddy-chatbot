"""
Main Flask application entry point
"""

import os
from app import create_app
from app.config import config_by_name

# Get configuration from environment or default to development
config_name = os.environ.get("FLASK_ENV", "development")
config_class = config_by_name.get(config_name, config_by_name["development"])

# Create Flask app
app = create_app(config_class)


@app.shell_context_processor
def make_shell_context():
    """Add models to shell context for flask shell"""
    from app.models.database import db, Conversation, RAGPipelineLog
    return {"db": db, "Conversation": Conversation, "RAGPipelineLog": RAGPipelineLog}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
