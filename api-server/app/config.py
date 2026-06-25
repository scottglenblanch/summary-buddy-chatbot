"""
Flask configuration for different environments
"""

import os
from datetime import timedelta
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Resolve configuration before any config class is read.
#   1. Load secrets from .env into the environment.
#   2. Load the environment-specific YAML (api-server/config/dev.yaml or prod.yaml),
#      expanding ${VAR} references with the secrets loaded above, and push the
#      resulting values into the environment for the config classes to consume.
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_ENV_NAME = os.environ.get("FLASK_ENV", "development")

load_dotenv(_BACKEND_ROOT / ".env")

_CONFIG_FILE = "prod.yaml" if _ENV_NAME == "production" else "dev.yaml"
_config_path = _BACKEND_ROOT / "config" / _CONFIG_FILE
if _config_path.exists():
    with open(_config_path, encoding="utf-8") as _f:
        _raw_config = yaml.safe_load(_f) or {}
    for _key, _value in _raw_config.items():
        if isinstance(_value, str):
            _value = os.path.expandvars(_value)
        # Don't override variables already set in the real environment (e.g. by nx).
        os.environ.setdefault(_key, "" if _value is None else str(_value))


class Config:
    """Base configuration"""
    
    # Flask
    ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = os.environ.get("FLASK_DEBUG", False)
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/summary_buddy_chatbot"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # File uploads (default 500MB; override with MAX_UPLOAD_MB)
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", 500)) * 1024 * 1024
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    
    # AWS
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET = os.environ.get("AWS_S3_BUCKET", "")
    AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", "")

    # Vector DB (PostgreSQL + pgvector)
    PGVECTOR_URL = os.environ.get(
        "PGVECTOR_URL",
        os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:postgres@postgres:5432/summary_buddy_chatbot"
        )
    )
    PGVECTOR_COLLECTION_NAME = os.environ.get("PGVECTOR_COLLECTION_NAME", "summary_buddy")
    
    # RAG Settings
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "200"))
    RAG_K_RESULTS = int(os.environ.get("RAG_K_RESULTS", "4"))
    TEXT_FILE_MAX_CHARS = int(os.environ.get("TEXT_FILE_MAX_CHARS", "50000"))


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    # Local PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@postgres:5432/summary_buddy_chatbot"
    )


class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Ensure secret key is set in production
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Production database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable must be set in production")
    
    # Production OpenAI key
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable must be set in production")


# Config mapping
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
