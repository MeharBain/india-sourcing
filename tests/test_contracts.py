"""Cross-connector contracts that apply automatically to registered connectors."""

import socket
import sys
import time
from collections.abc import Callable, Iterable, Iterator
from contextlib import ExitStack, contextmanager
from datetime import UTC, date, datetime
from types import ModuleType
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlmodel import Session

from src.connectors import REGISTERED_CONNECTORS
from src.connectors.base import Connector, FetchTarget
from src.core.models import RawDoc, Signal
from src.core.provenance import missing_provenance


class ParseSideEffectError(AssertionError):
    """Raised when a parser crosses its pure-function boundary."""


def _reject_side_effect(*args: object, **kwargs: object) -> None:
    raise ParseSideEffectError("parse() attempted network, database, or clock access")


class _BlockedDateTime(datetime):
    @classmethod
    def now(cls, tz: object = None) -> datetime:
        _reject_side_effect()

    @classmethod
    def utcnow(cls) -> datetime:
        _reject_side_effect()

    @classmethod
    def today(cls) -> datetime:
        _reject_side_effect()


class _BlockedDate(date):
    @classmethod
    def today(cls) -> date:
        _reject_side_effect()


@contextmanager
def _pure_parse_boundary(connector: object) -> Iterator[None]:
    module = __import__(connector.__class__.__module__, fromlist=["*"])
    module_prefix = module.__name__.rsplit(".", 1)[0]
    connector_modules = [
        loaded_module
        for name, loaded_module in sys.modules.items()
        if loaded_module is not None
        and (name == module.__name__ or name.startswith(f"{module_prefix}."))
    ]
    replacements: list[tuple[ModuleType, str, object]] = []
    for connector_module in connector_modules:
        for name, value in vars(connector_module).items():
            if value is datetime:
                replacements.append((connector_module, name, _BlockedDateTime))
            elif value is date:
                replacements.append((connector_module, name, _BlockedDate))

    patchers = [
        patch.object(socket, "socket", side_effect=_reject_side_effect),
        patch.object(socket, "create_connection", side_effect=_reject_side_effect),
        patch.object(time, "time", side_effect=_reject_side_effect),
        patch.object(time, "monotonic", side_effect=_reject_side_effect),
        patch.object(time, "perf_counter", side_effect=_reject_side_effect),
        patch.object(time, "process_time", side_effect=_reject_side_effect),
        patch("sqlmodel.Session.exec", new=_reject_side_effect),
        patch("sqlmodel.Session.add", new=_reject_side_effect),
        patch("sqlmodel.Session.add_all", new=_reject_side_effect),
        patch("sqlmodel.Session.commit", new=_reject_side_effect),
        patch("sqlalchemy.orm.Session.execute", new=_reject_side_effect),
        patch("sqlalchemy.orm.Session.add", new=_reject_side_effect),
        patch("sqlalchemy.orm.Session.add_all", new=_reject_side_effect),
        patch("sqlalchemy.orm.Session.commit", new=_reject_side_effect),
        *[
            patch.object(owner, name, replacement)
            for owner, name, replacement in replacements
        ],
    ]
    with ExitStack() as stack:
        for patcher in patchers:
            stack.enter_context(patcher)
        yield


def _registered_signal_rows() -> Iterable[tuple[str, Signal, RawDoc]]:
    """Yield signals and their resolved raw documents from connector fixtures."""

    for connector_class in REGISTERED_CONNECTORS:
        connector = connector_class()
        raw_docs = {raw_doc.id: raw_doc for raw_doc in connector.contract_raw_docs()}
        with _pure_parse_boundary(connector):
            signals = list(connector.contract_signals())
        for signal in signals:
            resolved_raw_doc = raw_docs.get(signal.raw_doc_id)
            assert resolved_raw_doc is not None, (
                f"raw_doc_id {signal.raw_doc_id} does not resolve"
            )
            yield connector.key, signal, resolved_raw_doc


def test_every_registered_connector_returns_signals_with_reachable_provenance() -> None:
    rows = list(_registered_signal_rows())

    assert any(connector.key == "birac_big" for connector in REGISTERED_CONNECTORS)
    assert sum(key == "birac_big" for key, _, _ in rows) == 102
    assert rows
    for _, signal, raw_doc in rows:
        assert missing_provenance(signal, raw_doc) == ()


class _SideEffectConnector(Connector):
    key = "side_effect_probe"
    cadence = "weekly"

    def __init__(self, action: Callable[[], object]) -> None:
        self.action = action

    def discover(self) -> Iterable[FetchTarget]:
        return []

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        self.action()
        return []

    def contract_raw_docs(self) -> Iterable[RawDoc]:
        return []

    def contract_signals(self) -> Iterable[Signal]:
        return []


class _MissingContractFixturesConnector(Connector):
    key = "missing_contract_fixtures"
    cadence = "weekly"

    def discover(self) -> Iterable[FetchTarget]:
        return []

    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        return []


def test_connector_missing_contract_fixtures_fails_clearly() -> None:
    with pytest.raises(
        TypeError,
        match=r"abstract methods? 'contract_raw_docs', 'contract_signals'",
    ):
        _MissingContractFixturesConnector()


@pytest.mark.parametrize(
    "action",
    [
        lambda: socket.create_connection(("example.invalid", 443)),
        lambda: Session().commit(),
        lambda: time.time(),
    ],
    ids=["network", "database", "clock"],
)
def test_parse_purity_boundary_rejects_network_database_and_clock_reads(
    action: Callable[[], object],
) -> None:
    connector = _SideEffectConnector(action)
    raw_doc = RawDoc(
        source_id=uuid4(),
        url="https://example.invalid/fixture.pdf",
        fetched_at=datetime(2026, 9, 9, tzinfo=UTC),
        content_hash="a" * 64,
        storage_path="fixture.pdf",
        http_status=200,
    )

    with pytest.raises(ParseSideEffectError), _pure_parse_boundary(connector):
        list(connector.parse(raw_doc))
