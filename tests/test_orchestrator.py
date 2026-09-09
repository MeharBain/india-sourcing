"""Tests for connector discovery, orchestration, and source health isolation."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest

from src.connectors.base import Connector, FetchTarget, discover_connectors
from src.connectors.orchestrator import run_connectors
from src.core.models import RawDoc, Signal, Source


class _Result:
    def __init__(self, value: Source | None) -> None:
        self.value = value

    def one_or_none(self) -> Source | None:
        return self.value


class FakeSession:
    def __init__(self, sources: Iterable[Source]) -> None:
        self.sources = {source.key: source for source in sources}
        self.signals: list[Signal] = []
        self.commits = 0
        self.rollbacks = 0

    def exec(self, statement: Any) -> _Result:
        params = statement.compile().params
        key = next(value for name, value in params.items() if name.startswith("key_"))
        return _Result(self.sources.get(key))

    def add(self, instance: object) -> None:
        if isinstance(instance, Signal):
            self.signals.append(instance)

    def add_all(self, instances: Iterable[object]) -> None:
        for instance in instances:
            self.add(instance)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _source(key: str) -> Source:
    return Source(
        key=key,
        name=key,
        tier=1,
        category="grant",
        cadence="weekly",
        health_status="unknown",
    )


def _raw_doc(source_id: UUID, url: str) -> RawDoc:
    return RawDoc(
        source_id=source_id,
        url=url,
        fetched_at=datetime(2026, 9, 9, tzinfo=UTC),
        content_hash=uuid4().hex,
        storage_path="data/raw_docs/test",
        http_status=200,
    )


class GoodConnector(Connector):
    key = "good"
    cadence = "weekly"

    def discover(self) -> Iterable[FetchTarget]:
        return [FetchTarget("https://good.example/awards.pdf")]

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        return [
            Signal(
                signal_type="grant_award",
                source_id=doc.source_id,
                event_date=date(2026, 1, 1),
                payload={"name": "Good Bio"},
                raw_doc_id=doc.id,
                confidence=1.0,
                extractor_version="test-v1",
            )
        ]


class DiscoverFailureConnector(Connector):
    key = "discover_failure"
    cadence = "weekly"

    def discover(self) -> Iterable[FetchTarget]:
        raise RuntimeError("listing changed")

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        return []


class ParseFailureConnector(Connector):
    key = "parse_failure"
    cadence = "weekly"

    def discover(self) -> Iterable[FetchTarget]:
        return [FetchTarget("https://bad.example/awards.pdf")]

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        raise ValueError("table changed")


def _fetcher(*, url: str, source_id: UUID, session: object) -> RawDoc:
    return _raw_doc(source_id, url)


def test_registry_discovers_concrete_connector_subclasses(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = tmp_path / "example_connectors"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "connector.py").write_text(
        "from src.connectors.base import Connector\n"
        "\n"
        "class ExampleConnector(Connector):\n"
        "    key = 'example'\n"
        "    cadence = 'weekly'\n"
        "    def discover(self):\n"
        "        return []\n"
        "    def parse(self, doc):\n"
        "        return []\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    connectors = discover_connectors("example_connectors")

    assert [connector.key for connector in connectors] == ["example"]


def test_discover_failure_does_not_stop_other_connectors_and_records_health() -> None:
    failed = _source(DiscoverFailureConnector.key)
    good = _source(GoodConnector.key)
    session = FakeSession([failed, good])

    run_connectors(
        session=session,
        connectors=[DiscoverFailureConnector(), GoodConnector()],
        fetcher=_fetcher,
    )

    assert [signal.payload for signal in session.signals] == [{"name": "Good Bio"}]
    assert failed.health_status == "failed"
    assert failed.consecutive_failures == 1
    assert failed.last_error == "listing changed"
    assert failed.last_failure_at is not None
    assert good.health_status == "healthy"
    assert good.consecutive_failures == 0
    assert good.last_success_at is not None
    assert session.commits == 2


def test_parse_failure_does_not_stop_other_connectors_and_records_health() -> None:
    failed = _source(ParseFailureConnector.key)
    good = _source(GoodConnector.key)
    session = FakeSession([failed, good])

    run_connectors(
        session=session,
        connectors=[ParseFailureConnector(), GoodConnector()],
        fetcher=_fetcher,
    )

    assert [signal.payload for signal in session.signals] == [{"name": "Good Bio"}]
    assert failed.health_status == "failed"
    assert failed.consecutive_failures == 1
    assert failed.last_error == "table changed"
    assert failed.last_failure_at is not None
    assert good.health_status == "healthy"
    assert good.consecutive_failures == 0
    assert good.last_success_at is not None
    assert session.commits == 2


def test_three_consecutive_failures_then_success_resets_source_health() -> None:
    source = _source(ParseFailureConnector.key)
    session = FakeSession([source])

    for _ in range(3):
        run_connectors(
            session=session,
            connectors=[ParseFailureConnector()],
            fetcher=_fetcher,
        )

    assert source.health_status == "failed"
    assert source.consecutive_failures == 3

    recovered = GoodConnector()
    recovered.key = ParseFailureConnector.key
    run_connectors(session=session, connectors=[recovered], fetcher=_fetcher)

    assert source.health_status == "healthy"
    assert source.consecutive_failures == 0
    assert source.last_success_at is not None
    assert session.commits == 4
