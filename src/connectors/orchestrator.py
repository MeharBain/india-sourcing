"""Run connectors while isolating and recording per-source failures."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Iterable
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


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _source_for_connector(session: Session, connector: Connector) -> Source:
    source = session.exec(select(Source).where(Source.key == connector.key)).one_or_none()
    if source is None:
        raise LookupError(f"No source row exists for connector key {connector.key!r}")
    return source


def _failure_count(health_status: str) -> int:
    try:
        health = json.loads(health_status)
    except (json.JSONDecodeError, TypeError):
        return 0
    if health.get("status") != "failed":
        return 0
    count = health.get("consecutive_failures", 0)
    return count if isinstance(count, int) and count >= 0 else 0


def _healthy_status() -> str:
    return json.dumps(
        {"status": "healthy", "consecutive_failures": 0},
        separators=(",", ":"),
    )


def _failed_status(source: Source, error: Exception) -> str:
    return json.dumps(
        {
            "status": "failed",
            "consecutive_failures": _failure_count(source.health_status) + 1,
            "error_type": type(error).__name__,
            "message": str(error),
        },
        separators=(",", ":"),
    )


def _validate_signal(signal: Signal, source: Source, raw_docs: dict[UUID, RawDoc]) -> None:
    if signal.company_id is not None:
        raise ValueError("Connectors must not set signal.company_id")
    if signal.source_id != source.id:
        raise ValueError("Connector returned a signal for a different source")
    raw_doc = raw_docs.get(signal.raw_doc_id)
    if raw_doc is None or raw_doc.source_id != source.id:
        raise ValueError("Connector returned a signal without a fetched source RawDoc")


def run_connectors(
    *,
    session: Session,
    connectors: Iterable[Connector] | None = None,
    fetcher: Fetcher = storage.fetch,
    now: Now = _utc_now,
) -> None:
    """Run each connector independently and persist its signals or failure health."""

    if connectors is None:
        from src.connectors import REGISTERED_CONNECTORS

        connectors = REGISTERED_CONNECTORS

    for connector in connectors:
        source: Source | None = None
        try:
            source = _source_for_connector(session, connector)
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
            signals = [
                signal
                for raw_doc in raw_docs
                for signal in connector.parse(raw_doc)
            ]
            for signal in signals:
                _validate_signal(signal, source, raw_docs_by_id)

            session.add_all(signals)
            source.health_status = _healthy_status()
            source.last_success_at = now()
            session.add(source)
            session.commit()
        except Exception as error:
            session.rollback()
            logger.exception("Connector %s failed", connector.key)
            if source is None:
                continue
            source.health_status = _failed_status(source, error)
            session.add(source)
            session.commit()
