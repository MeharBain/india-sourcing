"""Add the signal classification review table.

Revision ID: 5a3e7b1c9d02
Revises: c4b9e2d7a106
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5a3e7b1c9d02"
down_revision: str | None = "c4b9e2d7a106"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the global signal classification review table."""
    op.create_table(
        "classification_review",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("signal_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.String(),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("resolved_class", sa.String(), nullable=True),
        sa.Column("resolved_by", sa.String(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'resolved', 'undecidable')",
            name="ck_classification_review_status",
        ),
        sa.CheckConstraint(
            "reason IN ('ambiguous_class', 'low_confidence')",
            name="ck_classification_review_reason",
        ),
        sa.CheckConstraint(
            "resolved_class IN ('company_private_limited', 'company_llp', "
            "'company_opc', 'person', 'ambiguous')",
            name="ck_classification_review_resolved_class",
        ),
        sa.CheckConstraint(
            "(status = 'resolved' "
            "AND resolved_class IS NOT NULL "
            "AND resolved_by IS NOT NULL "
            "AND resolved_at IS NOT NULL) "
            "OR (status <> 'resolved' "
            "AND resolved_class IS NULL "
            "AND resolved_by IS NULL "
            "AND resolved_at IS NULL)",
            name="ck_classification_review_resolution_consistency",
        ),
        sa.ForeignKeyConstraint(["signal_id"], ["signal.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("signal_id", name="uq_classification_review_signal_id"),
    )


def downgrade() -> None:
    """Drop the signal classification review table."""
    op.drop_table("classification_review")
