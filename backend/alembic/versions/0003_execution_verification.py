"""Add execution_result and verification_result columns to investigation_runs table.

Revision ID: 0003_execution_verification
Revises: 0002_investigation_runs
Create Date: 2026-09-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_execution_verification"
down_revision: Union[str, None] = "0002_investigation_runs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "investigation_runs",
        sa.Column("execution_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "investigation_runs",
        sa.Column("verification_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("investigation_runs", "verification_result")
    op.drop_column("investigation_runs", "execution_result")
