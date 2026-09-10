"""Define the pipeline's persistent SQLModel records."""

from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    """A customer-specific thesis and scoring configuration."""

    __tablename__ = "tenant"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    thesis_doc: str | None = Field(default=None, sa_column=Column(Text))
    weight_overrides: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )


class Source(SQLModel, table=True):
    """A registered public data source and its latest health state."""

    __tablename__ = "source"
    __table_args__ = (
        CheckConstraint(
            "health_status IN ('healthy', 'failed', 'unknown')",
            name="ck_source_health_status",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    key: str = Field(unique=True, index=True)
    name: str
    tier: int
    category: str
    cadence: str
    last_success_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )
    health_status: str = Field(
        default="unknown",
        sa_column=Column(String, nullable=False, server_default="unknown"),
    )
    consecutive_failures: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default="0"),
    )
    last_error: str | None = Field(default=None, sa_column=Column(Text))
    last_failure_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )


class RawDoc(SQLModel, table=True):
    """An immutable, content-addressed snapshot fetched from a source."""

    __tablename__ = "raw_doc"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    source_id: UUID = Field(foreign_key="source.id", index=True)
    url: str = Field(sa_column=Column(Text, nullable=False))
    fetched_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    content_hash: str = Field(unique=True, index=True)
    storage_path: str = Field(sa_column=Column(Text, nullable=False))
    http_status: int


class Company(SQLModel, table=True):
    """The canonical company half of the dual entity spine."""

    __tablename__ = "company"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cin: str | None = Field(default=None, unique=True, index=True)
    legal_name: str
    display_name: str
    incorporation_date: date | None = None
    state: str | None = None
    city: str | None = None
    website: str | None = Field(default=None, sa_column=Column(Text))
    lifecycle_status: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


class Person(SQLModel, table=True):
    """The canonical person half of the dual entity spine."""

    __tablename__ = "person"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    din: str | None = Field(default=None, unique=True, index=True)
    full_name: str
    normalized_name: str = Field(index=True)


class Signal(SQLModel, table=True):
    """An append-only sourced fact awaiting or carrying company resolution."""

    __tablename__ = "signal"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_signal_confidence_range",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: UUID | None = Field(default=None, foreign_key="company.id", index=True)
    signal_type: str = Field(index=True)
    source_id: UUID = Field(foreign_key="source.id", index=True)
    event_date: date
    payload: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    raw_doc_id: UUID = Field(foreign_key="raw_doc.id", index=True)
    confidence: float
    extractor_version: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


class ClassificationReview(SQLModel, table=True):
    """A global human classification decision for one sourced signal."""

    __tablename__ = "classification_review"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'resolved', 'undecidable')",
            name="ck_classification_review_status",
        ),
        CheckConstraint(
            "reason IN ('ambiguous_class', 'low_confidence')",
            name="ck_classification_review_reason",
        ),
        CheckConstraint(
            "resolved_class IN ('company_private_limited', 'company_llp', "
            "'company_opc', 'person', 'ambiguous')",
            name="ck_classification_review_resolved_class",
        ),
        CheckConstraint(
            "(status = 'pending' "
            "AND resolved_class IS NULL "
            "AND reviewed_by IS NULL "
            "AND reviewed_at IS NULL) "
            "OR (status = 'resolved' "
            "AND resolved_class IS NOT NULL "
            "AND reviewed_by IS NOT NULL "
            "AND reviewed_at IS NOT NULL) "
            "OR (status = 'undecidable' "
            "AND resolved_class IS NULL "
            "AND reviewed_by IS NOT NULL "
            "AND reviewed_at IS NOT NULL)",
            name="ck_classification_review_resolution_consistency",
        ),
        UniqueConstraint("signal_id", name="uq_classification_review_signal_id"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    signal_id: UUID = Field(foreign_key="signal.id")
    status: str = Field(
        default="pending",
        sa_column=Column(String, nullable=False, server_default="pending"),
    )
    reason: str = Field(sa_column=Column(String, nullable=False))
    resolved_class: str | None = Field(default=None, sa_column=Column(String))
    reviewed_by: str | None = Field(default=None, sa_column=Column(String))
    reviewed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )
    notes: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


class CompanyAlias(SQLModel, table=True):
    """A source-observed name for a canonical company."""

    __tablename__ = "company_alias"

    company_id: UUID = Field(foreign_key="company.id", primary_key=True)
    name: str
    normalized_name: str = Field(primary_key=True, index=True)
    first_seen_source_id: UUID = Field(foreign_key="source.id")


class CompanyPerson(SQLModel, table=True):
    """A sourced relationship between the two canonical spine entities."""

    __tablename__ = "company_person"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_company_person_confidence_range",
        ),
    )

    company_id: UUID = Field(foreign_key="company.id", primary_key=True)
    person_id: UUID = Field(foreign_key="person.id", primary_key=True)
    role: str = Field(primary_key=True)
    source_ref: str = Field(sa_column=Column(Text, nullable=False))
    confidence: float


class ResolutionCandidate(SQLModel, table=True):
    """A proposed signal-to-company match and its resolution evidence."""

    __tablename__ = "resolution_candidate"
    __table_args__ = (
        CheckConstraint(
            "match_score >= 0.0 AND match_score <= 1.0",
            name="ck_resolution_candidate_match_score_range",
        ),
    )

    signal_id: UUID = Field(foreign_key="signal.id", primary_key=True)
    company_id: UUID = Field(foreign_key="company.id", primary_key=True)
    match_score: float
    features: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    decided_by: str | None = None
    decided_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )


class Score(SQLModel, table=True):
    """The latest deterministic company score for one tenant."""

    __tablename__ = "score"
    __table_args__ = (
        CheckConstraint("total >= 0.0 AND total <= 100.0", name="ck_score_total_range"),
    )

    company_id: UUID = Field(foreign_key="company.id", primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", primary_key=True)
    total: float = Field(sa_column=Column(Float, nullable=False))
    components: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    model_version: str
    computed_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))


class ReviewEvent(SQLModel, table=True):
    """An immutable human triage judgment scoped to one tenant."""

    __tablename__ = "review_event"
    __table_args__ = (
        CheckConstraint(
            "action IN ('interesting', 'not_for_us', 'already_known', 'data_wrong')",
            name="ck_review_event_action",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: UUID = Field(foreign_key="company.id", index=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)
    user_id: str
    action: str
    reason: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


class Watchlist(SQLModel, table=True):
    """A pre-incorporation awardee monitored for a later company match."""

    __tablename__ = "watchlist"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    person_id: UUID = Field(foreign_key="person.id", index=True)
    awarding_signal_id: UUID = Field(foreign_key="signal.id", unique=True, index=True)
    status: str = Field(default="active", index=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
