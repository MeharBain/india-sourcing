"""Add the resolved person link to signals.

Revision ID: 9d6f1e2a4b80
Revises: 5a3e7b1c9d02
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9d6f1e2a4b80"
down_revision: str | None = "5a3e7b1c9d02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add person resolution and permit both entity-link mutations."""
    op.add_column("signal", sa.Column("person_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_signal_person_id_person",
        "signal",
        "person",
        ["person_id"],
        ["id"],
    )
    op.create_index(op.f("ix_signal_person_id"), "signal", ["person_id"], unique=False)
    op.create_check_constraint(
        "ck_signal_single_entity",
        "signal",
        "company_id IS NULL OR person_id IS NULL",
    )

    op.execute("DROP TRIGGER IF EXISTS signal_append_only ON signal")
    op.execute(
        """
        CREATE TRIGGER signal_append_only
        BEFORE UPDATE OF
            id,
            signal_type,
            source_id,
            event_date,
            payload,
            raw_doc_id,
            confidence,
            extractor_version,
            created_at
        OR DELETE ON signal
        FOR EACH ROW
        EXECUTE FUNCTION reject_immutable_table_mutation()
        """
    )


def downgrade() -> None:
    """Remove person resolution and restore company-only mutable resolution."""
    op.execute("DROP TRIGGER IF EXISTS signal_append_only ON signal")
    op.drop_constraint("ck_signal_single_entity", "signal", type_="check")
    op.drop_index(op.f("ix_signal_person_id"), table_name="signal")
    op.drop_constraint(
        "fk_signal_person_id_person",
        "signal",
        type_="foreignkey",
    )
    op.drop_column("signal", "person_id")

    op.execute(
        """
        CREATE TRIGGER signal_append_only
        BEFORE UPDATE OF
            id,
            signal_type,
            source_id,
            event_date,
            payload,
            raw_doc_id,
            confidence,
            extractor_version,
            created_at
        OR DELETE ON signal
        FOR EACH ROW
        EXECUTE FUNCTION reject_immutable_table_mutation()
        """
    )
