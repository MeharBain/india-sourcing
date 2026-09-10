"""Discover configured BIRAC BIG cohorts and parse their immutable snapshots."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import yaml

from src.connectors.base import Connector, FetchTarget
from src.connectors.birac_big.parser import EXTRACTOR_VERSION, parse_big_awardees
from src.core.models import RawDoc, Signal

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCES_CONFIG = PROJECT_ROOT / "config" / "sources.yaml"
DEFAULT_SCORING_CONFIG = PROJECT_ROOT / "config" / "scoring.yaml"
FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURE_BY_URL = {
    "https://birac.nic.in/webcontent/1676014626_Final_list_of_BIG_21_Awardees.pdf": (
        "big_21.pdf"
    ),
    "https://birac.nic.in/webcontent/1759752792_big_24_awardees.pdf": "big_24.pdf",
}


class BiracBigConnector(Connector):
    """Connector for committed BIRAC Biotechnology Ignition Grant award lists."""

    key = "birac_big"
    cadence = "per_call"
    extractor_version = EXTRACTOR_VERSION

    def __init__(
        self,
        sources_config: Path = DEFAULT_SOURCES_CONFIG,
        scoring_config: Path = DEFAULT_SCORING_CONFIG,
    ) -> None:
        self.sources_config = sources_config
        self.classification_confidence = self._load_classification_confidence(
            scoring_config
        )

    @staticmethod
    def _load_classification_confidence(path: Path) -> dict[str, float]:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        values = config.get("applicant_classification_confidence")
        expected_keys = {"explicit_marker", "name_shape", "ambiguous"}
        if not isinstance(values, dict) or set(values) != expected_keys:
            raise ValueError(
                "applicant_classification_confidence must define "
                "explicit_marker, name_shape, and ambiguous"
            )
        if any(
            not isinstance(value, (int, float)) or not 0 <= value <= 1
            for value in values.values()
        ):
            raise ValueError(
                "applicant classification confidences must be numbers from 0 to 1"
            )
        return {key: float(value) for key, value in values.items()}

    def _source_config(self) -> dict[str, object]:
        registry = yaml.safe_load(self.sources_config.read_text(encoding="utf-8"))
        return next(source for source in registry["sources"] if source["key"] == self.key)

    def discover(self) -> Iterable[FetchTarget]:
        """Return explicitly configured cohort URLs without making a network request."""
        urls = self._source_config().get("artifact_urls")
        if not isinstance(urls, list) or not urls or not all(isinstance(url, str) for url in urls):
            raise ValueError("birac_big.artifact_urls must be a non-empty list of URLs")
        return tuple(FetchTarget(url) for url in urls)

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        """Extract awardee signals deterministically from one immutable cohort PDF."""
        return parse_big_awardees(doc, self.classification_confidence)

    def contract_raw_docs(self) -> Iterable[RawDoc]:
        """Return the two committed cohort PDFs as deterministic contract fixtures."""
        source_id = uuid5(NAMESPACE_URL, self.key)
        raw_docs = []
        for url in self._source_config()["artifact_urls"]:
            path = FIXTURE_DIR / FIXTURE_BY_URL[url]
            raw_docs.append(
                RawDoc(
                    id=uuid5(NAMESPACE_URL, url),
                    source_id=source_id,
                    url=url,
                    fetched_at=datetime(2026, 9, 10, tzinfo=UTC),
                    content_hash=hashlib.sha256(path.read_bytes()).hexdigest(),
                    storage_path=str(path),
                    http_status=200,
                )
            )
        return tuple(raw_docs)

    def contract_signals(self) -> Iterable[Signal]:
        """Parse every committed contract fixture."""
        return tuple(
            signal for raw_doc in self.contract_raw_docs() for signal in self.parse(raw_doc)
        )
