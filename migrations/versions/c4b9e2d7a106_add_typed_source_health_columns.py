"""Add typed source health columns.

Revision ID: c4b9e2d7a106
Revises: f9fda2306f8a
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4b9e2d7a106"
down_revision: str | None = "f9fda2306f8a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Replace JSON-in-text source health with typed state columns."""
    op.alter_column(
        "source",
        "health_status",
        existing_type=sa.String(),
        server_default="unknown",
        existing_nullable=False,
    )
    op.add_column(
        "source",
        sa.Column(
            "consecutive_failures",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column("source", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column(
        "source",
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_check_constraint(
        "ck_source_health_status",
        "source",
        "health_status IN ('healthy', 'failed', 'unknown')",
    )


def downgrade() -> None:
    """Restore the original text-only source health schema."""
    op.drop_constraint("ck_source_health_status", "source", type_="check")
    op.drop_column("source", "last_failure_at")
    op.drop_column("source", "last_error")
    op.drop_column("source", "consecutive_failures")
    op.alter_column(
        "source",
        "health_status",
        existing_type=sa.String(),
        server_default=None,
        existing_nullable=False,
    )
