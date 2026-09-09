"""Initial OpsPilot tables.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("workflow_stage", sa.String(length=32), nullable=False),
        sa.Column("service_id", sa.String(length=64), nullable=False),
        sa.Column("service_name", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.String(length=64), nullable=False),
        sa.Column("duration_label", sa.String(length=32), nullable=False),
        sa.Column("elapsed_seconds", sa.Integer(), nullable=False),
        sa.Column("trigger", sa.Text(), nullable=False),
        sa.Column("affected_services", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("blast_radius", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "incident_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("incident_id", sa.String(length=32), nullable=False),
        sa.Column("timestamp", sa.String(length=32), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incident_events_incident_id", "incident_events", ["incident_id"])
    op.create_table(
        "log_entries",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("incident_id", sa.String(length=32), nullable=False),
        sa.Column("timestamp", sa.String(length=32), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("service", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_log_entries_incident_id", "log_entries", ["incident_id"])
    op.create_table(
        "deployments",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("service_id", sa.String(length=64), nullable=False),
        sa.Column("service_name", sa.String(length=64), nullable=False),
        sa.Column("author", sa.String(length=64), nullable=False),
        sa.Column("author_email", sa.String(length=128), nullable=False),
        sa.Column("deployed_at", sa.String(length=64), nullable=False),
        sa.Column("time_label", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("commit", sa.String(length=64), nullable=False),
        sa.Column("commit_message", sa.Text(), nullable=False),
        sa.Column("files_changed", sa.String(length=64), nullable=False),
        sa.Column("diff_excerpt", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("deployments")
    op.drop_index("ix_log_entries_incident_id", table_name="log_entries")
    op.drop_table("log_entries")
    op.drop_index("ix_incident_events_incident_id", table_name="incident_events")
    op.drop_table("incident_events")
    op.drop_table("incidents")
