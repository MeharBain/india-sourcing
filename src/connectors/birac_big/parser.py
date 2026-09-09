"""Extract BIRAC BIG awardee signals from raw cohort documents."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import pdfplumber

from src.core.models import RawDoc, Signal
from src.core.provenance import build_signal

REFERENCE_PATTERN = r"BIRAC/[A-Z]+\d+/BIG-?\d+/\d+"
_REFERENCE = re.compile(REFERENCE_PATTERN)
_CATEGORY = re.compile(
    r"^(?:Category|Categories|Theme)\s*(?:-|–|—|�)\s*(.+)$",
    re.IGNORECASE,
)
_PRIVATE_LIMITED = re.compile(
    r"(?:private\s+limited|pvt\.?\s*\.?ltd\.?)$",
    re.IGNORECASE,
)
_LLP = re.compile(r"\bllp\.?$", re.IGNORECASE)
_OPC = re.compile(r"\bopc\b", re.IGNORECASE)
_HONORIFIC = re.compile(r"^(?:dr|mr|mrs|ms|prof)\.?\s+", re.IGNORECASE)
_NAME_TOKEN = re.compile(r"[A-Za-z]+|[A-Za-z]\.")
_BUSINESS_WORDS = {
    "biosciences",
    "biotech",
    "diagnostics",
    "healthcare",
    "healthtech",
    "innovations",
    "labs",
    "lifesciences",
    "research",
    "sciences",
    "solutions",
    "technologies",
}
EXTRACTOR_VERSION = "birac-big-v1"


@dataclass(frozen=True, slots=True)
class _AwardeeRow:
    category: str
    serial_number: int
    reference: str
    applicant_name: str
    final_score: float | None


def _normalise_space(value: str) -> str:
    return " ".join(value.split())


def _category_from_text(text: str) -> str | None:
    for line in text.splitlines():
        match = _CATEGORY.match(_normalise_space(line))
        if match:
            return _normalise_space(match.group(1)).replace("Me dical", "Medical")
    return None


def _main_table(page: object) -> list[list[str | None]]:
    tables = page.extract_tables()
    if not tables:
        raise ValueError("BIRAC page contains no extractable table")
    return max(
        tables,
        key=lambda table: sum(
            "BIRAC/" in (cell or "") for row in table for cell in row
        ),
    )


def _row_cells(rows: Sequence[Sequence[str | None]]) -> list[str]:
    return [cell for row in rows for cell in row if cell and cell.strip()]


def _reference_from_cells(cells: Sequence[str]) -> str:
    suffix = next(
        (
            _normalise_space(cell)
            for cell in cells
            if re.fullmatch(r"\d+/\d+", _normalise_space(cell))
        ),
        None,
    )
    for cell in cells:
        if "BIRAC/" not in cell:
            continue
        normalised = cell.replace("BIG-\n", "BIG")
        compact = re.sub(r"\s+", "", normalised)
        match = _REFERENCE.search(compact)
        if match:
            return match.group(0)
        if compact.endswith("BIG-") and suffix:
            candidate = f"{compact[:-1]}{suffix}"
            if _REFERENCE.fullmatch(candidate):
                return candidate
    raise ValueError(f"Could not extract BIRAC reference from cells: {cells!r}")


def _applicant_from_cells(cells: Sequence[str]) -> str:
    fragments: list[str] = []
    for cell in cells:
        value = _normalise_space(cell)
        if not value or "BIRAC/" in value:
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", value) or re.fullmatch(r"\d+/\d+", value):
            continue
        if any(
            marker in value.casefold()
            for marker in (
                "proposal reference",
                "applicant name",
                "final score",
                "s. no",
                "s.no",
            )
        ):
            continue
        if value.startswith("*") or _CATEGORY.match(value):
            continue
        reference = _REFERENCE.search(re.sub(r"\s+", "", value))
        if reference:
            value = value[reference.end() :].strip()
        if value and value not in fragments:
            fragments.append(value)
    applicant = _normalise_space(" ".join(fragments))
    if not applicant:
        raise ValueError(f"Could not extract applicant name from cells: {cells!r}")
    return applicant


def _serial_from_cells(cells: Sequence[str]) -> int:
    for cell in cells:
        value = _normalise_space(cell)
        if re.fullmatch(r"\d+", value):
            return int(value)
    raise ValueError(f"Could not extract serial number from cells: {cells!r}")


def _score_from_cells(cells: Sequence[str], *, has_scores: bool) -> float | None:
    if not has_scores:
        return None
    for cell in cells:
        value = _normalise_space(cell)
        if re.fullmatch(r"\d+\.\d{1,2}", value):
            return float(value)
    raise ValueError(f"Could not extract final score from cells: {cells!r}")


def _rows_from_table(
    table: Sequence[Sequence[str | None]],
    *,
    category: str,
    has_scores: bool,
) -> list[_AwardeeRow]:
    starts = [
        index
        for index, row in enumerate(table)
        if any("BIRAC/" in (cell or "") for cell in row)
    ]
    rows = []
    for position, start in enumerate(starts):
        stop = starts[position + 1] if position + 1 < len(starts) else len(table)
        cells = _row_cells(table[start:stop])
        rows.append(
            _AwardeeRow(
                category=category,
                serial_number=_serial_from_cells(cells),
                reference=_reference_from_cells(cells),
                applicant_name=_applicant_from_cells(cells),
                final_score=_score_from_cells(cells, has_scores=has_scores),
            )
        )
    return rows


def _classify_applicant(applicant: str) -> str:
    if _OPC.search(applicant):
        return "company_opc"
    if _LLP.search(applicant):
        return "company_llp"
    if _PRIVATE_LIMITED.search(applicant):
        return "company_private_limited"
    if _HONORIFIC.search(applicant):
        return "person"

    tokens = _NAME_TOKEN.findall(applicant)
    words = {token.rstrip(".").casefold() for token in tokens}
    conservative_person_shape = (
        2 <= len(tokens) <= 4
        and "-" not in applicant
        and not words.intersection(_BUSINESS_WORDS)
        and _normalise_space(" ".join(tokens)).replace(" .", ".") == applicant
    )
    return "person" if conservative_person_shape else "ambiguous"


def _publication_timestamp(url: str) -> str:
    match = re.search(r"/(\d{10})[_-]", url)
    if not match:
        raise ValueError("BIRAC artifact URL does not contain a Unix timestamp prefix")
    published_at = datetime.fromtimestamp(int(match.group(1)), tz=UTC)
    return published_at.isoformat().replace("+00:00", "Z")


def _event_year(reference: str) -> int:
    suffix = int(reference.rsplit("/", 1)[1])
    return 2000 + suffix


def parse_big_awardees(doc: RawDoc) -> Iterable[Signal]:
    """Parse supported BIRAC BIG cohort layouts into fully-provenanced signals."""
    path = Path(doc.storage_path)
    with pdfplumber.open(path) as pdf:
        page_texts = [page.extract_text(x_tolerance=2, y_tolerance=3) or "" for page in pdf.pages]
        document_text = "\n".join(page_texts)
        has_scores = "Final Score" in document_text
        provisional = bool(re.search(r"(?im)^\*\s*Subject\b", document_text))
        current_category: str | None = None
        rows: list[_AwardeeRow] = []
        for page, page_text in zip(pdf.pages, page_texts, strict=True):
            current_category = _category_from_text(page_text) or current_category
            if current_category is None:
                raise ValueError("BIRAC award rows appeared before a category heading")
            rows.extend(
                _rows_from_table(
                    _main_table(page),
                    category=current_category,
                    has_scores=has_scores,
                )
            )

    if not rows:
        raise ValueError("BIRAC document contained no awardee rows")

    published_at = _publication_timestamp(doc.url)
    for row in rows:
        year = _event_year(row.reference)
        cohort_number = re.search(r"/BIG-?(\d+)/", row.reference)
        if cohort_number is None:
            raise ValueError(f"Reference does not contain a BIG cohort: {row.reference}")
        applicant_class = _classify_applicant(row.applicant_name)
        yield build_signal(
            signal_type=f"birac_big_{applicant_class}",
            source_id=doc.source_id,
            event_date=date(year, 1, 1),
            payload={
                "serial_number": row.serial_number,
                "proposal_reference_number": row.reference,
                "applicant_name": row.applicant_name,
                "category": row.category,
                "cohort": f"BIG-{cohort_number.group(1)}",
                "final_score": row.final_score,
                "provisional": provisional,
                "event_date_precision": "year",
                "event_year_source": "proposal_reference_number",
                "list_published_at": published_at,
            },
            raw_doc_id=doc.id,
            confidence=1.0,
            extractor_version=EXTRACTOR_VERSION,
        )
