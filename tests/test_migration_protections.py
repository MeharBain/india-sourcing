"""Offline checks for database-level immutable-table protections."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

INITIAL_MIGRATION = (
    Path(__file__).parents[1] / "migrations" / "versions" / "f9fda2306f8a_create_initial_schema.py"
)
PERSON_ID_MIGRATION = (
    Path(__file__).parents[1]
    / "migrations"
    / "versions"
    / "9d6f1e2a4b80_add_signal_person_id.py"
)


def _migration_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_raw_doc_update_and_delete_are_rejected_by_trigger() -> None:
    migration = _migration_source(INITIAL_MIGRATION)

    assert "RAISE EXCEPTION '% is immutable; % is not allowed'" in migration
    assert "BEFORE UPDATE OR DELETE ON raw_doc" in migration
    assert "DROP TRIGGER IF EXISTS raw_doc_immutable ON raw_doc" in migration


def test_signal_fact_updates_and_deletes_are_rejected_but_resolution_is_allowed() -> None:
    migration = _migration_source(PERSON_ID_MIGRATION)
    signal_trigger = migration.split("CREATE TRIGGER signal_append_only", 1)[1].split('"""', 1)[0]

    assert "BEFORE UPDATE OF" in signal_trigger
    assert "OR DELETE ON signal" in signal_trigger
    assert "payload" in signal_trigger
    assert "raw_doc_id" in signal_trigger
    assert "company_id" not in signal_trigger
    assert "person_id" not in signal_trigger
    assert "DROP TRIGGER IF EXISTS signal_append_only ON signal" in migration


def test_signal_person_id_update_succeeds_but_signal_type_update_is_rejected() -> None:
    migration = _migration_source(PERSON_ID_MIGRATION)
    signal_trigger = migration.split("CREATE TRIGGER signal_append_only", 1)[1].split('"""', 1)[0]
    protected_block = signal_trigger.split("BEFORE UPDATE OF", 1)[1].split(
        "OR DELETE ON signal", 1
    )[0]
    protected_columns = [
        line.strip().rstrip(",") for line in protected_block.splitlines() if line.strip()
    ]
    assert "signal_type" in protected_columns
    assert "person_id" not in protected_columns

    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE signal ("
                "id TEXT PRIMARY KEY, company_id TEXT, person_id TEXT, signal_type TEXT, "
                "source_id TEXT, event_date TEXT, payload TEXT, raw_doc_id TEXT, "
                "confidence REAL, extractor_version TEXT, created_at TEXT)"
            )
        )
        connection.execute(
            text(
                f"CREATE TRIGGER signal_append_only BEFORE UPDATE OF "
                f"{', '.join(protected_columns)} ON signal "
                "BEGIN SELECT RAISE(ABORT, 'signal is immutable'); END"
            )
        )
        connection.execute(
            text(
                "INSERT INTO signal (id, signal_type) VALUES ('signal-1', 'original')"
            )
        )
        connection.execute(
            text("UPDATE signal SET person_id = 'person-1' WHERE id = 'signal-1'")
        )
        assert connection.execute(
            text("SELECT person_id FROM signal WHERE id = 'signal-1'")
        ).scalar_one() == "person-1"

    with (
        pytest.raises(IntegrityError, match="signal is immutable"),
        engine.begin() as connection,
    ):
        connection.execute(
            text("UPDATE signal SET signal_type = 'changed' WHERE id = 'signal-1'")
        )
