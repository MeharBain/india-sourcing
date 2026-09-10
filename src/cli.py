"""Command-line entry points for operational pipeline tasks."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import yaml
from dotenv import load_dotenv
from sqlalchemy import func
from sqlmodel import Session, create_engine, select

from src.connectors.birac_big.connector import (
    DEFAULT_SOURCES_CONFIG,
    FIXTURE_BY_URL,
    FIXTURE_DIR,
    BiracBigConnector,
)
from src.connectors.orchestrator import run_connectors
from src.core.models import RawDoc, Source, Tenant
from src.core.storage import DEFAULT_STORAGE_DIR, ingest_bytes

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TENANT_NAME = "India sourcing"


def _database_url() -> str:
    load_dotenv(PROJECT_ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set; create the ignored .env file first")
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def _birac_config(path: Path = DEFAULT_SOURCES_CONFIG) -> dict[str, object]:
    registry = yaml.safe_load(path.read_text(encoding="utf-8"))
    return next(source for source in registry["sources"] if source["key"] == "birac_big")


def _seed_source(session: Session) -> Source:
    existing = session.exec(select(Source).where(Source.key == "birac_big")).one_or_none()
    if existing is not None:
        return existing

    config = _birac_config()
    source = Source(
        key=str(config["key"]),
        name=str(config["name"]),
        tier=int(config["tier"]),
        category=str(config["category"]),
        cadence=str(config["cadence"]),
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


def _seed_tenant(session: Session, name: str) -> Tenant:
    existing = session.exec(select(Tenant).where(Tenant.name == name)).first()
    if existing is not None:
        return existing

    tenant = Tenant(name=name)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


def _raw_doc_count(session: Session, source_id: UUID) -> int:
    statement = select(func.count()).select_from(RawDoc).where(RawDoc.source_id == source_id)
    return int(session.exec(statement).one())


def run_offline_ingestion(
    *,
    tenant_name: str,
    fetched_at: datetime,
    storage_dir: Path = DEFAULT_STORAGE_DIR,
) -> int:
    """Ingest committed BIRAC fixtures and run their connector without network access."""

    engine = create_engine(_database_url())
    with Session(engine) as session:
        source = _seed_source(session)
        _seed_tenant(session, tenant_name)
        raw_docs_before = _raw_doc_count(session, source.id)

        def fixture_fetcher(*, url: str, source_id: UUID, session: Session) -> RawDoc:
            fixture_name = FIXTURE_BY_URL.get(url)
            if fixture_name is None:
                raise LookupError(f"No committed BIRAC fixture is mapped to {url!r}")
            return ingest_bytes(
                content=(FIXTURE_DIR / fixture_name).read_bytes(),
                source_id=source_id,
                url=url,
                fetched_at=fetched_at,
                session=session,
                storage_dir=storage_dir,
            )

        summary = run_connectors(
            session=session,
            connectors=[BiracBigConnector],
            fetcher=fixture_fetcher,
        )

        session.expire_all()
        source = session.exec(select(Source).where(Source.key == "birac_big")).one()
        raw_docs_created = _raw_doc_count(session, source.id) - raw_docs_before

        print(f"raw_doc rows created: {raw_docs_created}")
        print(f"documents parsed: {summary.documents_parsed}")
        print(f"documents skipped: {summary.documents_skipped}")
        print(f"signal rows created: {summary.signals_persisted}")
        print(f"connectors failed: {summary.connectors_failed}")
        print(f"birac_big health_status: {source.health_status}")
        print(f"birac_big consecutive_failures: {source.consecutive_failures}")
        return 0 if source.health_status == "healthy" else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tenant-name",
        default=DEFAULT_TENANT_NAME,
        help=f"tenant row to ensure exists (default: {DEFAULT_TENANT_NAME!r})",
    )
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=DEFAULT_STORAGE_DIR,
        help=f"content-addressed raw-document directory (default: {DEFAULT_STORAGE_DIR})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    return run_offline_ingestion(
        tenant_name=args.tenant_name,
        fetched_at=datetime.now(UTC),
        storage_dir=args.storage_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
