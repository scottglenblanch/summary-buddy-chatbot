"""
Health check endpoint
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="")

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return jsonify({"status": "ok", "message": "API is running"}), 200
