"""Initial migration - Create Conversation and RAGPipelineLog tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Conversation table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('sources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'])

    # Create RAGPipelineLog table
    op.create_table(
        'rag_pipeline_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('chunks_created', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rag_pipeline_logs_status', 'rag_pipeline_logs', ['status'])
    op.create_index('ix_rag_pipeline_logs_started_at', 'rag_pipeline_logs', ['started_at'])


def downgrade() -> None:
    op.drop_index('ix_rag_pipeline_logs_started_at', table_name='rag_pipeline_logs')
    op.drop_index('ix_rag_pipeline_logs_status', table_name='rag_pipeline_logs')
    op.drop_table('rag_pipeline_logs')
    
    op.drop_index('ix_conversations_created_at', table_name='conversations')
    op.drop_table('conversations')
