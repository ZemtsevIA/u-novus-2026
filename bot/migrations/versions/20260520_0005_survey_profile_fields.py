"""add survey profile fields

Revision ID: 20260520_0005
Revises: 20260520_0004
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260520_0005"
down_revision = "20260520_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assessments", sa.Column("profile_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("assessments", sa.Column("search_params_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("assessment_questions", sa.Column("external_question_id", sa.String(length=255), nullable=True))
    op.add_column("assessment_questions", sa.Column("answer_value", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("assessment_questions", "answer_value")
    op.drop_column("assessment_questions", "external_question_id")
    op.drop_column("assessments", "search_params_json")
    op.drop_column("assessments", "profile_json")
