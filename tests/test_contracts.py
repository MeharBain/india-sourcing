"""Cross-connector contracts that apply automatically to registered connectors."""

from collections.abc import Iterable

from src.connectors import REGISTERED_CONNECTORS
from src.core.models import RawDoc, Signal
from src.core.provenance import missing_provenance


def _registered_signal_rows() -> Iterable[tuple[Signal, RawDoc]]:
    """Yield signals and their resolved raw documents from connector fixtures."""

    for connector in REGISTERED_CONNECTORS:
        raw_docs = {raw_doc.id: raw_doc for raw_doc in connector.contract_raw_docs()}
        for signal in connector.contract_signals():
            raw_doc = raw_docs.get(signal.raw_doc_id)
            assert raw_doc is not None, f"raw_doc_id {signal.raw_doc_id} does not resolve"
            yield signal, raw_doc


def test_every_registered_connector_returns_signals_with_reachable_provenance() -> None:
    for signal, raw_doc in _registered_signal_rows():
        assert missing_provenance(signal, raw_doc) == ()
