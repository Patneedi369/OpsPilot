"""Add investigation_runs table for persistent investigation tracking.

Revision ID: 0002_investigation_runs
Revises: 0001_initial
Create Date: 2026-09-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_investigation_runs"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "investigation_runs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("incident_id", sa.String(length=32), nullable=False),
        sa.Column("thread_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_step", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.String(length=64), nullable=False),
        sa.Column("completed_at", sa.String(length=64), nullable=True),
        sa.Column("final_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("approval_decision", sa.String(length=32), nullable=True),
        sa.Column("approval_actor", sa.String(length=64), nullable=True),
        sa.Column("approval_note", sa.Text(), nullable=True),
        sa.Column("approved_at", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigation_runs_incident_id", "investigation_runs", ["incident_id"])
    op.create_index("ix_investigation_runs_thread_id", "investigation_runs", ["thread_id"])
    op.create_index("ix_investigation_runs_status", "investigation_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_investigation_runs_status", table_name="investigation_runs")
    op.drop_index("ix_investigation_runs_thread_id", table_name="investigation_runs")
    op.drop_index("ix_investigation_runs_incident_id", table_name="investigation_runs")
    op.drop_table("investigation_runs")
