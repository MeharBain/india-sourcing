"""Apply exact-name resolution and route uncertain classifications for review."""

from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, select

from src.core.models import (
    ClassificationReview,
    Company,
    CompanyAlias,
    Person,
    Signal,
    Watchlist,
)
from src.resolve.normalize import normalize_name

_COMPANY_CLASSES = {
    "company_private_limited",
    "company_llp",
    "company_opc",
}
_APPLICANT_CLASSES = (
    "company_private_limited",
    "company_llp",
    "company_opc",
    "person",
    "ambiguous",
)


@dataclass(frozen=True, slots=True)
class ResolutionSummary:
    """Rows created by one minimal resolution pass."""

    signals_considered: int
    companies_created: int
    people_created: int
    aliases_created: int
    watchlist_rows_created: int
    classification_reviews_created: int


def _applicant_class(signal_type: str) -> str:
    for applicant_class in _APPLICANT_CLASSES:
        if signal_type == applicant_class or signal_type.endswith(f"_{applicant_class}"):
            return applicant_class
    raise ValueError(f"Unsupported applicant signal type: {signal_type!r}")


def _applicant_name(signal: Signal) -> str:
    applicant_name = signal.payload.get("applicant_name")
    if not isinstance(applicant_name, str) or not applicant_name.strip():
        raise ValueError(f"Signal {signal.id} has no applicant_name")
    return " ".join(applicant_name.split())


def resolve_signals(
    *,
    session: Session,
    review_confidence_threshold: float,
) -> ResolutionSummary:
    """Resolve all persisted applicant signals by exact normalized name."""
    signals = list(session.exec(select(Signal).order_by(Signal.event_date, Signal.id)).all())
    reviews = list(session.exec(select(ClassificationReview)).all())
    companies = list(session.exec(select(Company)).all())
    aliases = list(session.exec(select(CompanyAlias)).all())
    people = list(session.exec(select(Person)).all())
    watchlist_rows = list(session.exec(select(Watchlist)).all())

    reviews_by_signal = {review.signal_id: review for review in reviews}
    companies_by_id = {company.id: company for company in companies}
    companies_by_name = {
        alias.normalized_name: companies_by_id[alias.company_id] for alias in aliases
    }
    alias_keys = {(alias.company_id, alias.normalized_name) for alias in aliases}
    people_by_id = {person.id: person for person in people}
    people_by_name: dict[str, Person] = {}
    for person in people:
        people_by_name.setdefault(person.normalized_name, person)
    watchlist_by_signal = {row.awarding_signal_id: row for row in watchlist_rows}

    companies_created = 0
    people_created = 0
    aliases_created = 0
    watchlist_created = 0
    reviews_created = 0

    for signal in signals:
        parsed_class = _applicant_class(signal.signal_type)
        review = reviews_by_signal.get(signal.id)

        if review is None and (
            signal.confidence < review_confidence_threshold or parsed_class == "ambiguous"
        ):
            review = ClassificationReview(
                signal_id=signal.id,
                reason=(
                    "ambiguous_class" if parsed_class == "ambiguous" else "low_confidence"
                ),
            )
            session.add(review)
            reviews_by_signal[signal.id] = review
            reviews_created += 1
            signal.company_id = None
            continue

        effective_class = parsed_class
        if review is not None:
            if review.status in {"pending", "undecidable"}:
                signal.company_id = None
                continue
            if review.status != "resolved" or review.resolved_class is None:
                raise ValueError(
                    f"Classification review {review.id} has invalid state {review.status!r}"
                )
            effective_class = review.resolved_class

        applicant_name = _applicant_name(signal)
        normalized_name = normalize_name(applicant_name)
        if not normalized_name:
            raise ValueError(f"Signal {signal.id} applicant name normalizes to an empty value")

        if effective_class in _COMPANY_CLASSES:
            company = companies_by_name.get(normalized_name)
            if company is None and signal.company_id is not None:
                company = companies_by_id.get(signal.company_id)
            if company is None:
                company = Company(
                    legal_name=applicant_name,
                    display_name=applicant_name,
                    lifecycle_status="unknown",
                )
                session.add(company)
                session.flush()
                companies_by_id[company.id] = company
                companies_created += 1
            companies_by_name[normalized_name] = company

            alias_key = (company.id, normalized_name)
            if alias_key not in alias_keys:
                session.add(
                    CompanyAlias(
                        company_id=company.id,
                        name=applicant_name,
                        normalized_name=normalized_name,
                        first_seen_source_id=signal.source_id,
                    )
                )
                alias_keys.add(alias_key)
                aliases_created += 1
            signal.company_id = company.id
            continue

        if effective_class == "person":
            signal.company_id = None
            person = people_by_name.get(normalized_name)
            existing_watchlist = watchlist_by_signal.get(signal.id)
            if person is None and existing_watchlist is not None:
                person = people_by_id[existing_watchlist.person_id]
            if person is None:
                person = Person(full_name=applicant_name, normalized_name=normalized_name)
                session.add(person)
                session.flush()
                people_by_id[person.id] = person
                people_by_name[normalized_name] = person
                people_created += 1
            if existing_watchlist is None:
                watchlist = Watchlist(person_id=person.id, awarding_signal_id=signal.id)
                session.add(watchlist)
                watchlist_by_signal[signal.id] = watchlist
                watchlist_created += 1
            continue

        if effective_class == "ambiguous":
            signal.company_id = None
            continue

        raise ValueError(f"Unsupported resolved applicant class: {effective_class!r}")

    session.commit()
    return ResolutionSummary(
        signals_considered=len(signals),
        companies_created=companies_created,
        people_created=people_created,
        aliases_created=aliases_created,
        watchlist_rows_created=watchlist_created,
        classification_reviews_created=reviews_created,
    )
