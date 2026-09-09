"""Schema-level tests for the persistent data-model invariants."""

import pytest
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from src.core.models import Source, SQLModel


def _table(name: str):
    return SQLModel.metadata.tables[name]


def test_schema_contains_prd_tables_and_dual_spine() -> None:
    expected = {
        "tenant",
        "source",
        "raw_doc",
        "signal",
        "company",
        "company_alias",
        "person",
        "company_person",
        "resolution_candidate",
        "score",
        "review_event",
        "watchlist",
    }

    assert set(SQLModel.metadata.tables) == expected


def test_signal_provenance_is_required() -> None:
    columns = _table("signal").c

    for column_name in (
        "raw_doc_id",
        "source_id",
        "event_date",
        "extractor_version",
        "confidence",
    ):
        assert columns[column_name].nullable is False


def test_raw_doc_content_hash_is_unique() -> None:
    table = _table("raw_doc")
    content_hash = table.c.content_hash
    single_column_unique_constraints = {
        tuple(constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert content_hash.unique is True or (content_hash,) in single_column_unique_constraints


def test_signal_company_id_is_nullable() -> None:
    company_id = _table("signal").c.company_id

    assert company_id.nullable is True
    assert {foreign_key.target_fullname for foreign_key in company_id.foreign_keys} == {
        "company.id"
    }


def test_watchlist_links_person_to_awarding_signal() -> None:
    columns = _table("watchlist").c

    assert {key.target_fullname for key in columns.person_id.foreign_keys} == {"person.id"}
    assert {key.target_fullname for key in columns.awarding_signal_id.foreign_keys} == {"signal.id"}
    assert columns.status.nullable is False


def test_workflow_tables_are_tenant_scoped_but_tenant_is_not() -> None:
    assert "tenant_id" in _table("score").c
    assert "tenant_id" in _table("review_event").c
    assert "tenant_id" not in _table("tenant").c


def test_source_health_columns_are_typed_and_constrained() -> None:
    table = _table("source")
    columns = table.c

    assert isinstance(columns.health_status.type, String)
    assert columns.health_status.nullable is False
    assert str(columns.health_status.server_default.arg) == "unknown"
    assert isinstance(columns.consecutive_failures.type, Integer)
    assert columns.consecutive_failures.nullable is False
    assert str(columns.consecutive_failures.server_default.arg) == "0"
    assert isinstance(columns.last_error.type, Text)
    assert columns.last_error.nullable is True
    assert isinstance(columns.last_failure_at.type, DateTime)
    assert columns.last_failure_at.type.timezone is True
    assert columns.last_failure_at.nullable is True

    health_constraint = next(
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
        and constraint.name == "ck_source_health_status"
    )
    assert str(health_constraint.sqltext) == (
        "health_status IN ('healthy', 'failed', 'unknown')"
    )


def test_source_escalation_predicate_filters_by_consecutive_failures() -> None:
    engine = create_engine("sqlite://")
    Source.__table__.create(engine)
    failing = Source(
        key="failing",
        name="Failing source",
        tier=1,
        category="grant",
        cadence="weekly",
        health_status="failed",
        consecutive_failures=3,
    )
    healthy = Source(
        key="healthy",
        name="Healthy source",
        tier=1,
        category="grant",
        cadence="weekly",
        health_status="healthy",
        consecutive_failures=0,
    )

    with Session(engine) as session:
        session.add_all([failing, healthy])
        session.commit()
        escalated = session.exec(
            select(Source).where(Source.consecutive_failures >= 3)
        ).all()

    assert [source.key for source in escalated] == ["failing"]


def test_source_health_check_rejects_unexpected_status() -> None:
    engine = create_engine("sqlite://")
    Source.__table__.create(engine)
    source = Source(
        key="invalid",
        name="Invalid source",
        tier=1,
        category="grant",
        cadence="weekly",
        health_status="unexpected",
    )

    with Session(engine) as session:
        session.add(source)
        with pytest.raises(IntegrityError, match="ck_source_health_status"):
            session.commit()


def test_postgres_json_fields_use_jsonb() -> None:
    json_columns = {
        ("tenant", "weight_overrides"),
        ("signal", "payload"),
        ("resolution_candidate", "features"),
        ("score", "components"),
    }

    for table_name, column_name in json_columns:
        assert _table(table_name).c[column_name].type.__class__.__name__ == "JSONB"
