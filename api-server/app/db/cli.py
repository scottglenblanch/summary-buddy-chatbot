"""Database CLI commands for Flask"""

import click
from flask.cli import with_appcontext
from app.models.database import db


@click.group()
def cli():
    """Database management commands"""
    pass


@cli.command()
@with_appcontext
def init():
    """Initialize the database"""
    db.create_all()
    click.echo("✅ Database initialized successfully!")


@cli.command()
@with_appcontext
def drop():
    """Drop all database tables"""
    if click.confirm("Are you sure you want to drop all tables?"):
        db.drop_all()
        click.echo("✅ Database dropped successfully!")
    else:
        click.echo("Cancelled.")


@cli.command()
@with_appcontext
def seed():
    """Seed database with sample data"""
    from app.models.database import Conversation
    
    # Check if data already exists
    existing = Conversation.query.first()
    if existing:
        click.echo("Database already has data. Skipping seed.")
        return
    
    # Sample conversation
    sample_conversation = Conversation(
        question="What is this knowledge base about?",
        answer="This chatbot answers questions using documents you upload. Upload a PDF or text file to get started.",
        sources=["Getting Started"]
    )
    
    db.session.add(sample_conversation)
    db.session.commit()
    click.echo("✅ Database seeded successfully!")


if __name__ == "__main__":
    cli()
