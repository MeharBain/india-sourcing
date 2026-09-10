"""Behavioral tests for the minimal exact-name resolution pass."""

from collections import defaultdict
from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid4

import pytest

from src.core.models import (
    ClassificationReview,
    Company,
    CompanyAlias,
    Person,
    Signal,
    Watchlist,
)
from src.resolve.decide import backfill_signal_person_ids, resolve_signals
from src.resolve.normalize import normalize_name


class _Result:
    def __init__(self, rows: list[object]) -> None:
        self._rows = rows

    def all(self) -> list[object]:
        return list(self._rows)


class _FakeSession:
    def __init__(self, *rows: object) -> None:
        self.rows: defaultdict[type[object], list[object]] = defaultdict(list)
        for row in rows:
            self.rows[type(row)].append(row)
        self.commits = 0

    def exec(self, statement: Any) -> _Result:
        entity = statement.column_descriptions[0]["entity"]
        return _Result(self.rows[entity])

    def add(self, row: object) -> None:
        self.rows[type(row)].append(row)

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        self.commits += 1


def _signal(
    applicant_name: str,
    applicant_class: str,
    confidence: float,
    *,
    cohort: str = "BIG-21",
) -> Signal:
    return Signal(
        signal_type=f"birac_big_{applicant_class}",
        source_id=uuid4(),
        event_date=date(2024, 1, 1),
        payload={"applicant_name": applicant_name, "cohort": cohort},
        raw_doc_id=uuid4(),
        confidence=confidence,
        extractor_version="test-v1",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Acme Private Limited", "acme"),
        ("Acme Pvt Ltd", "acme"),
        ("Acme Pvt.Ltd.", "acme"),
        ("Acme LLP", "acme"),
        ("Acme OPC", "acme"),
        ("Acme OPC Private Limited", "acme"),
        ("  ACME,   Bio-Tech!  ", "acme bio tech"),
    ],
)
def test_normalize_name_strips_legal_suffixes_and_punctuation(
    value: str, expected: str
) -> None:
    assert normalize_name(value) == expected


def test_resolution_creates_entities_watchlist_and_cross_cohort_match() -> None:
    company_21 = _signal(
        "Acme Pvt.Ltd.",
        "company_private_limited",
        0.95,
        cohort="BIG-21",
    )
    company_24 = _signal(
        "ACME PRIVATE LIMITED",
        "company_private_limited",
        0.95,
        cohort="BIG-24",
    )
    person = _signal("Dr. Asha Rao", "person", 0.95)
    low_confidence = _signal("Ravi Kumar", "person", 0.50)
    ambiguous = _signal("Biopol Biosciences", "ambiguous", 0.30)
    session = _FakeSession(
        company_21,
        company_24,
        person,
        low_confidence,
        ambiguous,
    )

    summary = resolve_signals(session=session, review_confidence_threshold=0.70)

    companies = session.rows[Company]
    assert len(companies) == 1
    assert company_21.company_id == companies[0].id
    assert company_24.company_id == companies[0].id
    assert [(alias.name, alias.normalized_name) for alias in session.rows[CompanyAlias]] == [
        ("Acme Pvt.Ltd.", "acme")
    ]
    assert [(row.full_name, row.normalized_name) for row in session.rows[Person]] == [
        ("Dr. Asha Rao", "dr asha rao")
    ]
    assert [row.awarding_signal_id for row in session.rows[Watchlist]] == [person.id]
    assert person.person_id == session.rows[Person][0].id
    assert {(row.signal_id, row.reason) for row in session.rows[ClassificationReview]} == {
        (low_confidence.id, "low_confidence"),
        (ambiguous.id, "ambiguous_class"),
    }
    assert low_confidence.company_id is None
    assert ambiguous.company_id is None
    assert summary.companies_created == 1
    assert summary.people_created == 1
    assert summary.watchlist_rows_created == 1
    assert summary.classification_reviews_created == 2

    second_summary = resolve_signals(session=session, review_confidence_threshold=0.70)

    assert len(session.rows[Company]) == 1
    assert len(session.rows[Person]) == 1
    assert len(session.rows[Watchlist]) == 1
    assert len(session.rows[ClassificationReview]) == 2
    assert second_summary.companies_created == 0
    assert second_summary.people_created == 0
    assert second_summary.watchlist_rows_created == 0
    assert second_summary.classification_reviews_created == 0


def test_resolved_review_overrides_signal_type() -> None:
    signal = _signal("Dr. Maya Sen", "company_private_limited", 0.95)
    review = ClassificationReview(
        signal_id=signal.id,
        status="resolved",
        reason="ambiguous_class",
        resolved_class="person",
        reviewed_by="human-reviewer",
        reviewed_at=datetime(2026, 9, 10, tzinfo=UTC),
    )
    session = _FakeSession(signal, review)

    resolve_signals(session=session, review_confidence_threshold=0.70)

    assert session.rows[Company] == []
    assert [person.full_name for person in session.rows[Person]] == ["Dr. Maya Sen"]
    assert [row.awarding_signal_id for row in session.rows[Watchlist]] == [signal.id]
    assert signal.company_id is None
    assert signal.person_id == session.rows[Person][0].id


def test_pending_and_undecidable_reviews_create_nothing_or_requeue() -> None:
    pending_signal = _signal("Pending Private Limited", "company_private_limited", 0.95)
    undecidable_signal = _signal("Undecidable Person", "person", 0.95)
    pending = ClassificationReview(
        signal_id=pending_signal.id,
        status="pending",
        reason="low_confidence",
    )
    undecidable = ClassificationReview(
        signal_id=undecidable_signal.id,
        status="undecidable",
        reason="ambiguous_class",
        reviewed_by="human-reviewer",
        reviewed_at=datetime(2026, 9, 10, tzinfo=UTC),
    )
    session = _FakeSession(pending_signal, undecidable_signal, pending, undecidable)

    first = resolve_signals(session=session, review_confidence_threshold=0.70)
    second = resolve_signals(session=session, review_confidence_threshold=0.70)

    assert session.rows[Company] == []
    assert session.rows[Person] == []
    assert session.rows[Watchlist] == []
    assert session.rows[ClassificationReview] == [pending, undecidable]
    assert pending_signal.person_id is None
    assert undecidable_signal.person_id is None
    assert first.classification_reviews_created == 0
    assert second.classification_reviews_created == 0


def test_backfill_sets_signal_person_id_from_watchlist_once() -> None:
    signal = _signal("Dr. Asha Rao", "person", 0.95)
    person = Person(full_name="Dr. Asha Rao", normalized_name="dr asha rao")
    watchlist = Watchlist(person_id=person.id, awarding_signal_id=signal.id)
    session = _FakeSession(signal, person, watchlist)

    assert backfill_signal_person_ids(session=session) == 1
    assert signal.person_id == person.id
    assert backfill_signal_person_ids(session=session) == 0
