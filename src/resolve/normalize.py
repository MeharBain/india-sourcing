"""Normalize entity attributes before candidate generation."""

from __future__ import annotations

import re

_PUNCTUATION = re.compile(r"[\W_]+", re.UNICODE)
_LEGAL_SUFFIXES = (
    "private limited",
    "pvt ltd",
    "llp",
    "opc",
)


def normalize_name(value: str) -> str:
    """Return the exact-match key for a company or person name."""
    normalized = " ".join(_PUNCTUATION.sub(" ", value.casefold()).split())

    while normalized:
        for suffix in _LEGAL_SUFFIXES:
            if normalized == suffix:
                normalized = ""
                break
            marker = f" {suffix}"
            if normalized.endswith(marker):
                normalized = normalized[: -len(marker)].rstrip()
                break
        else:
            return normalized

    return normalized
