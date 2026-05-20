"""add courses payload to roadmaps

Revision ID: 20260520_0004
Revises: 20260520_0003
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260520_0004"
down_revision = "20260520_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "roadmaps",
        sa.Column(
            "courses_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.alter_column("roadmaps", "courses_json", server_default=None)


def downgrade() -> None:
    op.drop_column("roadmaps", "courses_json")

