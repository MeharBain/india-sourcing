"""Golden-fixture and discovery tests for the BIRAC BIG connector."""

from __future__ import annotations

import hashlib
import json
import re
import socket
from collections import Counter
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid5

import pytest
import yaml

from src.connectors.base import FetchTarget
from src.connectors.birac_big.connector import BiracBigConnector
from src.connectors.birac_big.parser import REFERENCE_PATTERN, _classify_applicant
from src.core.models import RawDoc, Signal

FIXTURES = Path(__file__).parent / "fixtures"
SOURCES_CONFIG = Path(__file__).parents[3] / "config" / "sources.yaml"
INCUBATORS_CONFIG = Path(__file__).parents[3] / "config" / "incubators.yaml"
SCORING_CONFIG = Path(__file__).parents[3] / "config" / "scoring.yaml"
FIXTURE_URLS = {
    "big_21.pdf": (
        "https://birac.nic.in/webcontent/"
        "1676014626_Final_list_of_BIG_21_Awardees.pdf"
    ),
    "big_24.pdf": "https://birac.nic.in/webcontent/1759752792_big_24_awardees.pdf",
}
FIXTURE_HASHES = {
    "big_21.pdf": "b0b560411cfe184eb02f38a2583bcab937d17603bc189350aa70d12557fefe4b",
    "big_24.pdf": "0bbc0815c3f997bcccc417eff7d18d20bcb31e0a1467a29fb0bbdb19f06fc38e",
}


@pytest.mark.parametrize("filename", ["big_21.pdf", "big_24.pdf"])
def test_fixture_bytes_match_reported_sha256(filename: str) -> None:
    actual = hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest()

    assert actual == FIXTURE_HASHES[filename]


def _raw_doc(filename: str) -> RawDoc:
    url = FIXTURE_URLS[filename]
    return RawDoc(
        id=uuid5(NAMESPACE_URL, url),
        source_id=uuid5(NAMESPACE_URL, BiracBigConnector.key),
        url=url,
        fetched_at=datetime(2026, 9, 10, tzinfo=UTC),
        content_hash=FIXTURE_HASHES[filename],
        storage_path=str(FIXTURES / filename),
        http_status=200,
    )


@lru_cache(maxsize=2)
def _signals(filename: str) -> tuple[Signal, ...]:
    return tuple(BiracBigConnector().parse(_raw_doc(filename)))


def _golden_summary(filename: str, expected: dict[str, object]) -> dict[str, object]:
    signals = _signals(filename)
    section_counts = Counter(signal.payload["category"] for signal in signals)
    class_distribution = Counter(
        signal.signal_type.removeprefix("birac_big_") for signal in signals
    )
    ambiguous = sorted(
        signal.payload["applicant_name"]
        for signal in signals
        if signal.signal_type == "birac_big_ambiguous"
    )
    by_row = {
        (signal.payload["category"], signal.payload["serial_number"]): signal
        for signal in signals
    }
    hand_verified_rows = []
    for expected_row in expected.get("hand_verified_rows", []):
        signal = by_row[(expected_row["category"], expected_row["serial_number"])]
        hand_verified_rows.append(
            {
                "category": signal.payload["category"],
                "serial_number": signal.payload["serial_number"],
                "proposal_reference_number": signal.payload[
                    "proposal_reference_number"
                ],
                "applicant_name": signal.payload["applicant_name"],
                "final_score": signal.payload["final_score"],
                "signal_type": signal.signal_type,
                "confidence": signal.confidence,
            }
        )

    return {
        "cohort": next(iter({signal.payload["cohort"] for signal in signals})),
        "signal_count": len(signals),
        "section_counts": dict(section_counts),
        "class_distribution": dict(sorted(class_distribution.items())),
        "ambiguous_applicants": ambiguous,
        "provisional_values": sorted(
            {signal.payload["provisional"] for signal in signals}
        ),
        "event_dates": sorted({signal.event_date.isoformat() for signal in signals}),
        "event_date_precision_values": sorted(
            {signal.payload["event_date_precision"] for signal in signals}
        ),
        "event_year_source_values": sorted(
            {signal.payload["event_year_source"] for signal in signals}
        ),
        "list_published_at_values": sorted(
            {signal.payload["list_published_at"] for signal in signals}
        ),
        "rows_with_scores": sum(
            signal.payload["final_score"] is not None for signal in signals
        ),
        "hand_verified_rows": hand_verified_rows,
    }


@pytest.mark.parametrize("filename", ["big_21.pdf", "big_24.pdf"])
def test_parser_matches_golden_fixture_summary(filename: str) -> None:
    expected_path = FIXTURES / filename.replace(".pdf", ".expected.json")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    assert _golden_summary(filename, expected) == expected


@pytest.mark.parametrize("filename", ["big_21.pdf", "big_24.pdf"])
def test_every_reference_and_partner_prefix_is_valid(filename: str) -> None:
    incubators = yaml.safe_load(INCUBATORS_CONFIG.read_text(encoding="utf-8"))[
        "incubators"
    ]

    for signal in _signals(filename):
        reference = signal.payload["proposal_reference_number"]
        assert re.fullmatch(REFERENCE_PATTERN, reference)
        prefix = reference.split("/", 2)[1].rstrip("0123456789")
        assert prefix in incubators, f"Unknown BIRAC partner prefix: {prefix}"


@pytest.mark.parametrize("filename", ["big_21.pdf", "big_24.pdf"])
def test_serials_are_contiguous_within_each_category(filename: str) -> None:
    serials_by_category: dict[str, list[int]] = {}
    for signal in _signals(filename):
        serials_by_category.setdefault(signal.payload["category"], []).append(
            signal.payload["serial_number"]
        )

    for serials in serials_by_category.values():
        assert serials == list(range(1, len(serials) + 1))


def test_big_21_has_verified_section_counts_in_document_order() -> None:
    counts = Counter(signal.payload["category"] for signal in _signals("big_21.pdf"))

    assert list(counts.items()) == [
        ("Medical Devices", 10),
        ("Diagnostics", 9),
        ("Industrial Biotechnology, Clean Energy & Environment", 9),
        ("Agriculture and allied areas", 14),
        ("Drugs and related areas", 9),
    ]


@pytest.mark.parametrize("filename", ["big_21.pdf", "big_24.pdf"])
def test_applicant_names_are_complete_and_do_not_contain_references(filename: str) -> None:
    dangling_suffix = re.compile(r"(?:Private|Pvt|and)$", re.IGNORECASE)
    reference = re.compile(REFERENCE_PATTERN)

    for signal in _signals(filename):
        applicant = signal.payload["applicant_name"]
        assert applicant
        assert "\n" not in applicant
        assert not dangling_suffix.search(applicant)
        assert not reference.search(applicant)


def test_scores_follow_each_cohort_schema() -> None:
    big_21_scores = [
        signal.payload["final_score"] for signal in _signals("big_21.pdf")
    ]
    big_24_scores = [
        signal.payload["final_score"] for signal in _signals("big_24.pdf")
    ]

    assert all(score is not None and 0 <= score <= 100 for score in big_21_scores)
    assert all(score is None for score in big_24_scores)


def test_applicant_classes_have_distinct_signal_types() -> None:
    signal_types = {
        signal.signal_type
        for filename in ("big_21.pdf", "big_24.pdf")
        for signal in _signals(filename)
    }

    assert signal_types == {
        "birac_big_ambiguous",
        "birac_big_company_llp",
        "birac_big_company_opc",
        "birac_big_company_private_limited",
        "birac_big_person",
    }


def _classification_confidence_config() -> dict[str, float]:
    config = yaml.safe_load(SCORING_CONFIG.read_text(encoding="utf-8"))
    return config["applicant_classification_confidence"]


@pytest.mark.parametrize(
    ("applicant", "expected_class", "expected_confidence"),
    [
        ("Aarogya Devices Private Limited", "company_private_limited", 0.95),
        ("Aarogya Devices LLP", "company_llp", 0.95),
        ("Aarogya Devices (OPC)", "company_opc", 0.95),
        ("Dr. Asha Rao", "person", 0.95),
        ("Asha Rao", "person", 0.50),
        ("Aarogya-Bio", "ambiguous", 0.30),
    ],
)
def test_applicant_classification_uses_configured_confidence_for_each_basis(
    applicant: str,
    expected_class: str,
    expected_confidence: float,
) -> None:
    result = _classify_applicant(applicant, _classification_confidence_config())

    assert result == (expected_class, expected_confidence)


@pytest.mark.parametrize("applicant", ["Inger Therapeutics", "Leofelis Instruments"])
def test_unknown_business_words_remain_low_confidence_person_inferences(
    applicant: str,
) -> None:
    """These are companies, but unknown shape stays low confidence.

    The classifier cannot know their true type; low confidence prevents either company
    from becoming a silent person entry in the incorporation watchlist.
    """
    applicant_class, confidence = _classify_applicant(
        applicant,
        _classification_confidence_config(),
    )

    assert applicant_class == "person"
    assert confidence == 0.50
    assert confidence < 0.95


def test_cohort_class_and_confidence_distributions_are_stable() -> None:
    config = yaml.safe_load(SCORING_CONFIG.read_text(encoding="utf-8"))
    threshold = config["review_confidence_threshold"]

    expected = {
        "big_21.pdf": {
            "classes": {
                "ambiguous": 2,
                "company_llp": 2,
                "company_private_limited": 32,
                "person": 15,
            },
            "confidences": {0.30: 2, 0.50: 8, 0.95: 41},
            "below_review_threshold": 10,
        },
        "big_24.pdf": {
            "classes": {
                "ambiguous": 2,
                "company_llp": 2,
                "company_opc": 1,
                "company_private_limited": 28,
                "person": 18,
            },
            "confidences": {0.30: 2, 0.95: 49},
            "below_review_threshold": 2,
        },
    }

    for filename, expected_distribution in expected.items():
        signals = _signals(filename)
        classes = Counter(
            signal.signal_type.removeprefix("birac_big_") for signal in signals
        )
        confidences = Counter(signal.confidence for signal in signals)
        below_threshold = sum(
            signal.confidence < threshold for signal in signals
        )

        assert len(signals) == 51
        assert dict(classes) == expected_distribution["classes"]
        assert dict(confidences) == expected_distribution["confidences"]
        assert below_threshold == expected_distribution["below_review_threshold"]


def test_review_confidence_threshold_is_configured_for_watchlist_review() -> None:
    config = yaml.safe_load(SCORING_CONFIG.read_text(encoding="utf-8"))

    assert config["review_confidence_threshold"] == 0.70


@pytest.mark.parametrize(
    ("filename", "event_date", "list_published_at"),
    [
        ("big_21.pdf", "2022-01-01", "2023-02-10T07:37:06Z"),
        ("big_24.pdf", "2024-01-01", "2025-10-06T12:13:12Z"),
    ],
)
def test_event_date_declares_year_precision_and_separate_publication_timestamp(
    filename: str,
    event_date: str,
    list_published_at: str,
) -> None:
    for signal in _signals(filename):
        assert signal.event_date.isoformat() == event_date
        assert signal.payload["event_date_precision"] == "year"
        assert signal.payload["event_year_source"] == "proposal_reference_number"
        assert signal.payload["list_published_at"] == list_published_at


@pytest.mark.parametrize("filename", ["big_21.pdf", "big_24.pdf"])
def test_all_signals_are_provisional_and_schema_conformant(filename: str) -> None:
    raw_doc = _raw_doc(filename)

    for signal in _signals(filename):
        assert signal.payload["provisional"] is True
        assert signal.company_id is None
        assert signal.source_id == raw_doc.source_id
        assert signal.raw_doc_id == raw_doc.id
        validated = Signal.model_validate(signal.model_dump())
        assert validated.model_dump() == signal.model_dump()


def test_discover_returns_exact_configured_targets_without_network() -> None:
    expected = [FetchTarget(url) for url in FIXTURE_URLS.values()]
    connector = BiracBigConnector()

    with (
        patch.object(socket, "socket", side_effect=AssertionError("network call")),
        patch.object(
            socket,
            "create_connection",
            side_effect=AssertionError("network call"),
        ),
    ):
        targets = list(connector.discover())

    assert targets == expected


def test_birac_source_config_records_listing_and_artifact_urls() -> None:
    sources = yaml.safe_load(SOURCES_CONFIG.read_text(encoding="utf-8"))["sources"]
    birac = next(source for source in sources if source["key"] == "birac_big")

    assert birac["verified"] is True
    assert birac["listing_url"] == "https://birac.nic.in/big.php"
    assert birac["artifact_urls"] == list(FIXTURE_URLS.values())
