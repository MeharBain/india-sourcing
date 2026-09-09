"""Tests for constructing signals with complete, grounded provenance."""

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

import pytest

from src.core.models import RawDoc, Signal
from src.core.provenance import (
    InvalidPayloadError,
    MissingProvenanceError,
    build_signal,
    missing_provenance,
)


def _signal_kwargs() -> dict[str, object]:
    return {
        "signal_type": "grant_award",
        "source_id": uuid4(),
        "event_date": date(2026, 1, 2),
        "payload": {"applicant": "Example Private Limited"},
        "raw_doc_id": uuid4(),
        "confidence": 0.95,
        "extractor_version": "birac-big-v1",
    }


def _raw_doc(raw_doc_id: UUID) -> RawDoc:
    return RawDoc(
        id=raw_doc_id,
        source_id=uuid4(),
        url="https://example.gov.in/awards.pdf",
        fetched_at=datetime(2026, 9, 9, tzinfo=UTC),
        content_hash="a" * 64,
        storage_path="data/raw_docs/aa",
        http_status=200,
    )


def test_build_signal_preserves_source_payload_and_reachable_provenance() -> None:
    kwargs = _signal_kwargs()
    signal = build_signal(**kwargs)
    raw_doc = _raw_doc(kwargs["raw_doc_id"])

    assert signal.payload == {"applicant": "Example Private Limited"}
    assert missing_provenance(signal, raw_doc) == ()


@pytest.mark.parametrize(
    "field,missing_value",
    [
        ("source_id", None),
        ("event_date", None),
        ("raw_doc_id", None),
        ("confidence", None),
        ("extractor_version", ""),
    ],
)
def test_build_signal_raises_for_missing_provenance(field: str, missing_value: object) -> None:
    kwargs = _signal_kwargs()
    kwargs[field] = missing_value

    with pytest.raises(MissingProvenanceError, match=field):
        build_signal(**kwargs)


def test_build_signal_rejects_infrastructure_metadata_in_payload() -> None:
    kwargs = _signal_kwargs()
    kwargs["payload"] = {"applicant": "Example Private Limited", "_provenance": {}}

    with pytest.raises(InvalidPayloadError, match="_provenance"):
        build_signal(**kwargs)


@pytest.mark.parametrize(
    "raw_doc,expected",
    [
        (None, ("raw_doc",)),
        (
            RawDoc(
                id=uuid4(),
                source_id=uuid4(),
                url="",
                fetched_at=datetime(2026, 9, 9, tzinfo=UTC),
                content_hash="b" * 64,
                storage_path="data/raw_docs/bb",
                http_status=200,
            ),
            ("raw_doc_id", "raw_doc.url"),
        ),
        (
            RawDoc(
                id=uuid4(),
                source_id=uuid4(),
                url="https://example.gov.in/awards.pdf",
                fetched_at=None,
                content_hash="c" * 64,
                storage_path="data/raw_docs/cc",
                http_status=200,
            ),
            ("raw_doc_id", "raw_doc.fetched_at"),
        ),
    ],
)
def test_missing_provenance_reports_unresolved_or_incomplete_raw_doc(
    raw_doc: RawDoc | None,
    expected: tuple[str, ...],
) -> None:
    signal = Signal(**_signal_kwargs())

    assert missing_provenance(signal, raw_doc) == expected
