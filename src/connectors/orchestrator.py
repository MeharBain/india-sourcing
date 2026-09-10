"""Run connectors while isolating and recording per-source failures."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from sqlmodel import Session, select

from src.connectors.base import Connector
from src.core import storage
from src.core.models import RawDoc, Signal, Source

logger = logging.getLogger(__name__)


class Fetcher(Protocol):
    def __call__(
        self,
        *,
        url: str,
        source_id: UUID,
        session: Session,
    ) -> RawDoc: ...


Now = Callable[[], datetime]


@dataclass(frozen=True, slots=True)
class RunSummary:
    """Aggregate committed work and isolated failures from one connector run."""

    documents_parsed: int
    documents_skipped: int
    signals_persisted: int
    connectors_failed: int


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _source_for_connector(session: Session, connector_key: str) -> Source:
    source = session.exec(select(Source).where(Source.key == connector_key)).one_or_none()
    if source is None:
        raise LookupError(f"No source row exists for connector key {connector_key!r}")
    return source


def _was_parsed(
    session: Session,
    raw_doc_id: UUID,
    extractor_version: str,
) -> bool:
    existing_signal_id = session.exec(
        select(Signal.id).where(
            Signal.raw_doc_id == raw_doc_id,
            Signal.extractor_version == extractor_version,
        ).limit(1)
    ).first()
    return existing_signal_id is not None


def _validate_signal(
    signal: Signal,
    source: Source,
    raw_docs: dict[UUID, RawDoc],
    extractor_version: str,
) -> None:
    if signal.company_id is not None:
        raise ValueError("Connectors must not set signal.company_id")
    if signal.source_id != source.id:
        raise ValueError("Connector returned a signal for a different source")
    raw_doc = raw_docs.get(signal.raw_doc_id)
    if raw_doc is None or raw_doc.source_id != source.id:
        raise ValueError("Connector returned a signal without a fetched source RawDoc")
    if signal.extractor_version != extractor_version:
        raise ValueError(
            "Connector returned a signal whose extractor_version differs from its declaration"
        )


def run_connectors(
    *,
    session: Session,
    connectors: Iterable[type[Connector]] | None = None,
    fetcher: Fetcher = storage.fetch,
    now: Now = _utc_now,
) -> RunSummary:
    """Run each connector independently and persist its signals or failure health."""

    if connectors is None:
        from src.connectors import REGISTERED_CONNECTORS

        connectors = REGISTERED_CONNECTORS

    documents_parsed = 0
    documents_skipped = 0
    signals_persisted = 0
    connectors_failed = 0
    for connector_class in connectors:
        source: Source | None = None
        try:
            source = _source_for_connector(session, connector_class.key)
            connector = connector_class()
            targets = list(connector.discover())
            raw_docs = []
            for target in targets:
                persisted_doc = fetcher(
                    url=target.url,
                    source_id=source.id,
                    session=session,
                )
                raw_docs.append(persisted_doc.model_copy())
            raw_docs_by_id = {raw_doc.id: raw_doc for raw_doc in raw_docs}
            signals = []
            connector_documents_parsed = 0
            connector_documents_skipped = 0
            for raw_doc in raw_docs:
                if _was_parsed(session, raw_doc.id, connector.extractor_version):
                    connector_documents_skipped += 1
                    continue
                parsed_signals = list(connector.parse(raw_doc))
                for signal in parsed_signals:
                    _validate_signal(
                        signal,
                        source,
                        raw_docs_by_id,
                        connector.extractor_version,
                    )
                signals.extend(parsed_signals)
                connector_documents_parsed += 1

            session.add_all(signals)
            if connector_documents_parsed or not connector_documents_skipped:
                source.health_status = "healthy"
                source.consecutive_failures = 0
                source.last_success_at = now()
                session.add(source)
            session.commit()
            documents_parsed += connector_documents_parsed
            documents_skipped += connector_documents_skipped
            signals_persisted += len(signals)
        except Exception as error:
            session.rollback()
            connectors_failed += 1
            logger.exception("Connector %s failed", connector_class.key)
            if source is None:
                continue
            source.health_status = "failed"
            source.consecutive_failures += 1
            source.last_error = str(error)
            source.last_failure_at = now()
            session.add(source)
            session.commit()

    return RunSummary(
        documents_parsed=documents_parsed,
        documents_skipped=documents_skipped,
        signals_persisted=signals_persisted,
        connectors_failed=connectors_failed,
    )
