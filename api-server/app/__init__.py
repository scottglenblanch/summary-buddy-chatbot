"""
Summary Buddy Chatbot - Flask Application
"""

from flask import Flask, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from flask_cors import CORS
from app.config import Config
from app.models.database import init_db, db


def create_app(config_class=Config) -> Flask:
    """
    Application factory pattern for Flask app creation.
    
    Args:
        config_class: Configuration class to use (dev, test, prod)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    init_db(app)
    
    # In development, ensure tables exist for a smooth first run.
    if app.config.get("ENV") == "development":
        with app.app_context():
            db.create_all()
    
    # Register blueprints
    from app.api.chatbot import chatbot_bp
    from app.api.admin import admin_bp
    from app.api.health import health_bp
    
    app.register_blueprint(chatbot_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(health_bp, url_prefix="/api")

    # Return a clean JSON 413 (instead of a generic 500) for oversized uploads
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(_error):
        limit_mb = app.config.get("MAX_CONTENT_LENGTH", 0) // (1024 * 1024)
        return jsonify({
            "status": "failed",
            "error": "File too large",
            "message": f"The uploaded file exceeds the maximum allowed size of {limit_mb} MB."
        }), 413
    
    # Register database CLI commands
    from app.db.cli import cli as db_cli
    app.cli.add_command(db_cli, name="db")
    
    return app
