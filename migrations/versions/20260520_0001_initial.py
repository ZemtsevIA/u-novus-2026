"""initial schema

Revision ID: 20260520_0001
Revises:
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260520_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    status_enum = postgresql.ENUM(
        "created",
        "waiting_topic",
        "questions_generated",
        "in_progress",
        "waiting_confirmation",
        "accepted",
        "rejected",
        "manually_selected",
        "completed",
        name="assessment_status",
    )
    status_enum.create(op.get_bind(), checkfirst=True)
    status_column_enum = postgresql.ENUM(
        "created",
        "waiting_topic",
        "questions_generated",
        "in_progress",
        "waiting_confirmation",
        "accepted",
        "rejected",
        "manually_selected",
        "completed",
        name="assessment_status",
        create_type=False,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)

    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=500), nullable=True),
        sa.Column("status", status_column_enum, nullable=False),
        sa.Column("current_question_index", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=50), nullable=True),
        sa.Column("level_title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("missing_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("accepted", sa.Boolean(), nullable=False),
        sa.Column("manual_level_selected", sa.Boolean(), nullable=False),
        sa.Column("miniapp_available", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessments_user_id"), "assessments", ["user_id"], unique=False)

    op.create_table(
        "assessment_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("question_order", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_assessment_questions_assessment_id"),
        "assessment_questions",
        ["assessment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_assessment_questions_assessment_id"), table_name="assessment_questions")
    op.drop_table("assessment_questions")
    op.drop_index(op.f("ix_assessments_user_id"), table_name="assessments")
    op.drop_table("assessments")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")
    sa.Enum(name="assessment_status").drop(op.get_bind(), checkfirst=True)
