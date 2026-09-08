"""Offline checks for database-level immutable-table protections."""

from pathlib import Path

MIGRATION = (
    Path(__file__).parents[1] / "migrations" / "versions" / "f9fda2306f8a_create_initial_schema.py"
)


def _migration_source() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_raw_doc_update_and_delete_are_rejected_by_trigger() -> None:
    migration = _migration_source()

    assert "RAISE EXCEPTION '% is immutable; % is not allowed'" in migration
    assert "BEFORE UPDATE OR DELETE ON raw_doc" in migration
    assert "DROP TRIGGER IF EXISTS raw_doc_immutable ON raw_doc" in migration


def test_signal_fact_updates_and_deletes_are_rejected_but_resolution_is_allowed() -> None:
    migration = _migration_source()
    signal_trigger = migration.split("CREATE TRIGGER signal_append_only", 1)[1].split('"""', 1)[0]

    assert "BEFORE UPDATE OF" in signal_trigger
    assert "OR DELETE ON signal" in signal_trigger
    assert "payload" in signal_trigger
    assert "raw_doc_id" in signal_trigger
    assert "company_id" not in signal_trigger
    assert "DROP TRIGGER IF EXISTS signal_append_only ON signal" in migration
