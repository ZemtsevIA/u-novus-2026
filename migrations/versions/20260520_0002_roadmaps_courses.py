"""add roadmaps and user courses

Revision ID: 20260520_0002
Revises: 20260520_0001
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260520_0002"
down_revision = "20260520_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    roadmap_status = postgresql.ENUM(
        "generated",
        "accepted",
        "rejected",
        name="roadmap_status",
    )
    roadmap_status.create(op.get_bind(), checkfirst=True)
    roadmap_status_column = postgresql.ENUM(
        "generated",
        "accepted",
        "rejected",
        name="roadmap_status",
        create_type=False,
    )

    op.create_table(
        "roadmaps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=500), nullable=False),
        sa.Column("level", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("items_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", roadmap_status_column, nullable=False),
        sa.Column("rejection_reason", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roadmaps_assessment_id"), "roadmaps", ["assessment_id"], unique=False)

    op.create_table(
        "user_courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("roadmap_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["roadmaps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "roadmap_id", name="uq_user_courses_user_roadmap"),
    )
    op.create_index(op.f("ix_user_courses_roadmap_id"), "user_courses", ["roadmap_id"], unique=False)
    op.create_index(op.f("ix_user_courses_user_id"), "user_courses", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_courses_user_id"), table_name="user_courses")
    op.drop_index(op.f("ix_user_courses_roadmap_id"), table_name="user_courses")
    op.drop_table("user_courses")
    op.drop_index(op.f("ix_roadmaps_assessment_id"), table_name="roadmaps")
    op.drop_table("roadmaps")
    postgresql.ENUM(name="roadmap_status").drop(op.get_bind(), checkfirst=True)

