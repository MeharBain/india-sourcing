"""Tests for connector discovery, orchestration, and source health isolation."""

from __future__ import annotations

import importlib
import sys
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


class _FixtureConnector(Connector):
    def contract_raw_docs(self) -> Iterable[RawDoc]:
        return []

    def contract_signals(self) -> Iterable[Signal]:
        return []


class GoodConnector(_FixtureConnector):
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


class DiscoverFailureConnector(_FixtureConnector):
    key = "discover_failure"
    cadence = "weekly"

    def discover(self) -> Iterable[FetchTarget]:
        raise RuntimeError("listing changed")

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        return []


class ParseFailureConnector(_FixtureConnector):
    key = "parse_failure"
    cadence = "weekly"

    def discover(self) -> Iterable[FetchTarget]:
        return [FetchTarget("https://bad.example/awards.pdf")]

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        raise ValueError("table changed")


class ConstructionFailureConnector(_FixtureConnector):
    key = "construction_failure"
    cadence = "weekly"

    def __init__(self) -> None:
        raise RuntimeError("scoring config malformed")

    def discover(self) -> Iterable[FetchTarget]:
        return []

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        return []


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
        "    def __init__(self):\n"
        "        raise RuntimeError('must not instantiate during registration')\n"
        "    def discover(self):\n"
        "        return []\n"
        "    def parse(self, doc):\n"
        "        return []\n"
        "    def contract_raw_docs(self):\n"
        "        return []\n"
        "    def contract_signals(self):\n"
        "        return []\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    connectors = discover_connectors("example_connectors")

    assert [connector.key for connector in connectors] == ["example"]


def test_registry_rejects_empty_class_key_without_instantiating(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = tmp_path / "empty_key_connectors"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "connector.py").write_text(
        "from src.connectors.base import Connector\n"
        "\n"
        "class EmptyKeyConnector(Connector):\n"
        "    key = '   '\n"
        "    cadence = 'weekly'\n"
        "    def __init__(self):\n"
        "        raise RuntimeError('must not instantiate during validation')\n"
        "    def discover(self):\n"
        "        return []\n"
        "    def parse(self, doc):\n"
        "        return []\n"
        "    def contract_raw_docs(self):\n"
        "        return []\n"
        "    def contract_signals(self):\n"
        "        return []\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(ValueError) as error:
        discover_connectors("empty_key_connectors")

    assert str(error.value) == "EmptyKeyConnector.key cannot be empty"


def test_registry_rejects_duplicate_class_keys_without_instantiating(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = tmp_path / "duplicate_key_connectors"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    connector_template = (
        "from src.connectors.base import Connector\n"
        "\n"
        "class {class_name}(Connector):\n"
        "    key = 'duplicate'\n"
        "    cadence = 'weekly'\n"
        "    def __init__(self):\n"
        "        raise RuntimeError('must not instantiate during validation')\n"
        "    def discover(self):\n"
        "        return []\n"
        "    def parse(self, doc):\n"
        "        return []\n"
        "    def contract_raw_docs(self):\n"
        "        return []\n"
        "    def contract_signals(self):\n"
        "        return []\n"
    )
    (package / "alpha.py").write_text(
        connector_template.format(class_name="AlphaConnector"), encoding="utf-8"
    )
    (package / "beta.py").write_text(
        connector_template.format(class_name="BetaConnector"), encoding="utf-8"
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(ValueError) as error:
        discover_connectors("duplicate_key_connectors")

    assert str(error.value) == (
        "Duplicate connector key 'duplicate': AlphaConnector and BetaConnector"
    )


def test_importing_registry_does_not_instantiate_connectors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.connectors as original_registry
    from src.connectors.birac_big.connector import BiracBigConnector

    def broken_constructor(self: object) -> None:
        raise RuntimeError("scoring config malformed")

    monkeypatch.setattr(BiracBigConnector, "__init__", broken_constructor)
    sys.modules.pop("src.connectors")
    try:
        imported_registry = importlib.import_module("src.connectors")
    finally:
        sys.modules["src.connectors"] = original_registry

    assert BiracBigConnector in imported_registry.REGISTERED_CONNECTORS


def test_discover_failure_does_not_stop_other_connectors_and_records_health() -> None:
    failed = _source(DiscoverFailureConnector.key)
    good = _source(GoodConnector.key)
    session = FakeSession([failed, good])

    run_connectors(
        session=session,
        connectors=[DiscoverFailureConnector, GoodConnector],
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
        connectors=[ParseFailureConnector, GoodConnector],
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
            connectors=[ParseFailureConnector],
            fetcher=_fetcher,
        )

    assert source.health_status == "failed"
    assert source.consecutive_failures == 3

    class RecoveredConnector(GoodConnector):
        key = ParseFailureConnector.key

    run_connectors(session=session, connectors=[RecoveredConnector], fetcher=_fetcher)

    assert source.health_status == "healthy"
    assert source.consecutive_failures == 0
    assert source.last_success_at is not None
    assert session.commits == 4


def test_construction_failure_does_not_stop_other_connectors_and_records_health() -> None:
    failed = _source(ConstructionFailureConnector.key)
    failed.consecutive_failures = 2
    good = _source(GoodConnector.key)
    session = FakeSession([failed, good])

    run_connectors(
        session=session,
        connectors=[ConstructionFailureConnector, GoodConnector],
        fetcher=_fetcher,
    )

    assert [signal.payload for signal in session.signals] == [{"name": "Good Bio"}]
    assert failed.health_status == "failed"
    assert failed.consecutive_failures == 3
    assert failed.last_error == "scoring config malformed"
