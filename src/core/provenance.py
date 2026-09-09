"""Construct signals and validate their direct and raw-document provenance."""

from collections.abc import Mapping
from datetime import date
from typing import Any
from uuid import UUID

from src.core.models import RawDoc, Signal

_DIRECT_PROVENANCE_FIELDS = (
    "source_id",
    "event_date",
    "raw_doc_id",
    "confidence",
    "extractor_version",
)


class MissingProvenanceError(ValueError):
    """Raised when a signal is missing required direct provenance."""


class InvalidPayloadError(ValueError):
    """Raised when source payload contains a reserved infrastructure key."""


def _missing_value(value: object) -> bool:
    return value is None or isinstance(value, str) and not value.strip()


def _reserved_payload_key(value: object, path: str = "payload") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str) and key.startswith("_"):
                return f"{path}.{key}"
            reserved = _reserved_payload_key(child, f"{path}.{key}")
            if reserved is not None:
                return reserved
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reserved = _reserved_payload_key(child, f"{path}[{index}]")
            if reserved is not None:
                return reserved
    return None


def build_signal(
    *,
    signal_type: str,
    source_id: UUID | None,
    event_date: date | None,
    payload: dict[str, Any],
    raw_doc_id: UUID | None,
    confidence: float | None,
    extractor_version: str | None,
) -> Signal:
    """Build a signal after enforcing direct provenance and payload boundaries."""

    values = {
        "source_id": source_id,
        "event_date": event_date,
        "raw_doc_id": raw_doc_id,
        "confidence": confidence,
        "extractor_version": extractor_version,
    }
    missing = tuple(name for name, value in values.items() if _missing_value(value))
    if missing:
        raise MissingProvenanceError(
            f"Signal is missing required provenance: {', '.join(missing)}"
        )

    reserved_key = _reserved_payload_key(payload)
    if reserved_key is not None:
        raise InvalidPayloadError(
            f"Payload key {reserved_key!r} is reserved; extracted-content keys cannot "
            "start with an underscore"
        )

    return Signal(
        signal_type=signal_type,
        source_id=source_id,
        event_date=event_date,
        payload=payload,
        raw_doc_id=raw_doc_id,
        confidence=confidence,
        extractor_version=extractor_version,
    )


def missing_provenance(signal: Signal, raw_doc: RawDoc | None) -> tuple[str, ...]:
    """Return missing direct fields and broken raw-document provenance links."""

    missing = [
        field
        for field in _DIRECT_PROVENANCE_FIELDS
        if _missing_value(getattr(signal, field, None))
    ]

    if raw_doc is None:
        missing.append("raw_doc")
        return tuple(missing)

    if signal.raw_doc_id != raw_doc.id:
        missing.append("raw_doc_id")
    if _missing_value(raw_doc.url):
        missing.append("raw_doc.url")
    if _missing_value(raw_doc.fetched_at):
        missing.append("raw_doc.fetched_at")

    return tuple(missing)
