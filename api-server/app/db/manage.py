"""Database initialization and management utilities"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.models.database import db


def init_db():
    """Initialize the database with schema"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully!")


def drop_db():
    """Drop all database tables"""
    app = create_app()
    with app.app_context():
        if input("Are you sure? This will delete all data (yes/no): ") == "yes":
            db.drop_all()
            print("✅ Database dropped successfully!")
        else:
            print("Cancelled.")


def seed_db():
    """Seed database with sample data"""
    app = create_app()
    with app.app_context():
        from app.models.database import Conversation
        
        # Check if data already exists
        existing = Conversation.query.first()
        if existing:
            print("Database already has data. Skipping seed.")
            return
        
        # Sample conversation
        sample_conversation = Conversation(
            question="What is this knowledge base about?",
            answer="This chatbot answers questions using documents you upload. Upload a PDF or text file to get started.",
            sources=["Getting Started"]
        )
        
        db.session.add(sample_conversation)
        db.session.commit()
        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management utilities")
    parser.add_argument(
        "command",
        choices=["init", "drop", "seed"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_db()
    elif args.command == "drop":
        drop_db()
    elif args.command == "seed":
        seed_db()
