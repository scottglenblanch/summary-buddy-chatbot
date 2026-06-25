"""
WSGI entry point for production deployments (Gunicorn)
"""

import os
from app import create_app
from app.config import config_by_name

config_name = os.environ.get("FLASK_ENV", "production")
config_class = config_by_name.get(config_name, config_by_name["production"])

# Create Flask app instance
app = create_app(config_class)

if __name__ == "__main__":
    app.run()
