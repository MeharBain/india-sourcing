"""Offline tests for polite HTTP collection and immutable raw-document storage."""

from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Thread
from typing import Any, Self
from urllib.error import URLError
from uuid import uuid4

import pytest

from src.core.models import RawDoc
from src.core.storage import (
    DomainRateLimiter,
    FetchError,
    HttpConfigurationError,
    RobotsDeniedError,
    fetch,
    ingest_bytes,
)


class FakeTime:
    def __init__(self) -> None:
        self.value = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.value += seconds

    def now(self) -> datetime:
        return datetime(2026, 9, 9, 12, 0, tzinfo=UTC)


class FakeResponse:
    def __init__(self, status: int, content: bytes) -> None:
        self.status = status
        self._content = content

    def read(self) -> bytes:
        return self._content

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        return None


class FakeTransport:
    def __init__(self, responses: dict[str, list[tuple[int, bytes] | Exception]]) -> None:
        self.responses = {url: deque(items) for url, items in responses.items()}
        self.requests: list[Any] = []

    def __call__(self, request: Any, timeout: float) -> FakeResponse:
        del timeout
        self.requests.append(request)
        outcome = self.responses[request.full_url].popleft()
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(*outcome)


class FakeResult:
    def __init__(self, value: RawDoc | None) -> None:
        self.value = value

    def first(self) -> RawDoc | None:
        return self.value


class FakeSession:
    def __init__(self) -> None:
        self.rows: dict[str, RawDoc] = {}
        self.added: list[RawDoc] = []
        self.commits = 0

    def exec(self, statement: Any) -> FakeResult:
        content_hash = statement._where_criteria[0].right.value
        return FakeResult(self.rows.get(content_hash))

    def add(self, row: RawDoc) -> None:
        self.added.append(row)
        self.rows[row.content_hash] = row

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, row: RawDoc) -> None:
        del row


def _fetch_kwargs(
    tmp_path: Path,
    transport: FakeTransport,
    fake_time: FakeTime,
    session: FakeSession | None = None,
) -> dict[str, Any]:
    return {
        "url": "https://example.gov.in/document.pdf",
        "source_id": uuid4(),
        "session": session or FakeSession(),
        "storage_dir": tmp_path,
        "transport": transport,
        "clock": fake_time.monotonic,
        "sleep": fake_time.sleep,
        "now": fake_time.now,
        "limiter": DomainRateLimiter(clock=fake_time.monotonic, sleep=fake_time.sleep),
        "robots_cache": {},
    }


def test_domain_rate_limiter_waits_two_seconds_without_real_sleep() -> None:
    fake_time = FakeTime()
    limiter = DomainRateLimiter(clock=fake_time.monotonic, sleep=fake_time.sleep)

    limiter.wait("https://example.gov.in/first")
    limiter.wait("https://example.gov.in/second")
    limiter.wait("https://other.gov.in/first")

    assert fake_time.sleeps == [2.0]


def test_domain_rate_limiter_does_not_block_a_different_domain() -> None:
    sleep_started = Event()
    release_sleep = Event()
    other_domain_finished = Event()

    def blocking_fake_sleep(seconds: float) -> None:
        assert seconds == 2.0
        sleep_started.set()
        release_sleep.wait(timeout=1.0)

    limiter = DomainRateLimiter(clock=lambda: 0.0, sleep=blocking_fake_sleep)
    limiter.wait("https://example.gov.in/first")

    same_domain = Thread(target=limiter.wait, args=("https://example.gov.in/second",))
    same_domain.start()
    assert sleep_started.wait(timeout=1.0)

    def wait_for_other_domain() -> None:
        limiter.wait("https://other.gov.in/first")
        other_domain_finished.set()

    other_domain = Thread(target=wait_for_other_domain)
    other_domain.start()
    assert other_domain_finished.wait(timeout=1.0)

    release_sleep.set()
    same_domain.join(timeout=1.0)
    other_domain.join(timeout=1.0)
    assert not same_domain.is_alive()
    assert not other_domain.is_alive()


def test_fetch_checks_robots_and_sends_configured_project_user_agent(tmp_path: Path) -> None:
    fake_time = FakeTime()
    transport = FakeTransport(
        {
            "https://example.gov.in/robots.txt": [(200, b"User-agent: *\nAllow: /\n")],
            "https://example.gov.in/document.pdf": [(200, b"document bytes")],
        }
    )

    fetch(**_fetch_kwargs(tmp_path, transport, fake_time))

    requested_urls = [request.full_url for request in transport.requests]
    assert requested_urls == [
        "https://example.gov.in/robots.txt",
        "https://example.gov.in/document.pdf",
    ]
    assert all("india-sourcing/" in request.get_header("User-agent") for request in transport.requests)
    assert all("SET_ME@example.invalid" in request.get_header("User-agent") for request in transport.requests)


def test_fetch_refuses_a_path_disallowed_by_robots(tmp_path: Path) -> None:
    fake_time = FakeTime()
    transport = FakeTransport(
        {
            "https://example.gov.in/robots.txt": [
                (200, b"User-agent: *\nDisallow: /document.pdf\n")
            ],
            "https://example.gov.in/document.pdf": [(200, b"must not be fetched")],
        }
    )

    with pytest.raises(RobotsDeniedError):
        fetch(**_fetch_kwargs(tmp_path, transport, fake_time))

    assert [request.full_url for request in transport.requests] == [
        "https://example.gov.in/robots.txt"
    ]


def test_fetch_retries_server_errors_with_exponential_backoff(tmp_path: Path) -> None:
    fake_time = FakeTime()
    transport = FakeTransport(
        {
            "https://example.gov.in/robots.txt": [(200, b"User-agent: *\nAllow: /\n")],
            "https://example.gov.in/document.pdf": [
                (500, b"temporary"),
                (502, b"temporary again"),
                (200, b"recovered"),
            ],
        }
    )

    fetch(**_fetch_kwargs(tmp_path, transport, fake_time))

    target_requests = [
        request for request in transport.requests if request.full_url.endswith("document.pdf")
    ]
    assert len(target_requests) == 3
    assert 1.0 in fake_time.sleeps
    assert 2.0 in fake_time.sleeps


def test_fetch_retries_transport_errors_with_exponential_backoff(tmp_path: Path) -> None:
    fake_time = FakeTime()
    transport = FakeTransport(
        {
            "https://example.gov.in/robots.txt": [(200, b"User-agent: *\nAllow: /\n")],
            "https://example.gov.in/document.pdf": [
                URLError("temporary network failure"),
                (200, b"recovered"),
            ],
        }
    )

    fetch(**_fetch_kwargs(tmp_path, transport, fake_time))

    target_requests = [
        request for request in transport.requests if request.full_url.endswith("document.pdf")
    ]
    assert len(target_requests) == 2
    assert 1.0 in fake_time.sleeps


def test_fetch_never_retries_client_errors(tmp_path: Path) -> None:
    fake_time = FakeTime()
    transport = FakeTransport(
        {
            "https://example.gov.in/robots.txt": [(200, b"User-agent: *\nAllow: /\n")],
            "https://example.gov.in/document.pdf": [(404, b"missing"), (200, b"unexpected")],
        }
    )

    with pytest.raises(FetchError, match="404"):
        fetch(**_fetch_kwargs(tmp_path, transport, fake_time))

    target_requests = [
        request for request in transport.requests if request.full_url.endswith("document.pdf")
    ]
    assert len(target_requests) == 1


def test_fetch_hashes_and_persists_bytes_without_duplicate_rows(tmp_path: Path) -> None:
    fake_time = FakeTime()
    session = FakeSession()
    transport = FakeTransport(
        {
            "https://example.gov.in/robots.txt": [(200, b"User-agent: *\nAllow: /\n")],
            "https://example.gov.in/document.pdf": [
                (200, b"same bytes"),
                (200, b"same bytes"),
            ],
        }
    )
    kwargs = _fetch_kwargs(tmp_path, transport, fake_time, session)

    first = fetch(**kwargs)
    second = fetch(**kwargs)

    assert first is second
    assert len(session.added) == 1
    assert session.commits == 1
    assert first.source_id == kwargs["source_id"]
    assert first.url == kwargs["url"]
    assert first.fetched_at == datetime(2026, 9, 9, 12, 0, tzinfo=UTC)
    assert first.http_status == 200
    assert first.content_hash == "58100dc8fc06562ce3e578231dc948e083520ee49c4b4ee5a5a28bb4b4003feb"
    assert Path(first.storage_path).read_bytes() == b"same bytes"
    assert Path(first.storage_path).is_relative_to(tmp_path)


def test_ingest_bytes_persists_local_fixture_once_with_remote_provenance(
    tmp_path: Path,
) -> None:
    fixture_path = tmp_path / "fixture.pdf"
    fixture_path.write_bytes(b"committed fixture bytes")
    storage_dir = tmp_path / "raw_docs"
    session = FakeSession()
    source_id = uuid4()
    origin_url = "https://example.gov.in/original-document.pdf"
    fetched_at = datetime(2026, 9, 10, 8, 30, tzinfo=UTC)

    first = ingest_bytes(
        content=fixture_path.read_bytes(),
        source_id=source_id,
        url=origin_url,
        fetched_at=fetched_at,
        session=session,
        storage_dir=storage_dir,
    )
    second = ingest_bytes(
        content=fixture_path.read_bytes(),
        source_id=source_id,
        url=origin_url,
        fetched_at=fetched_at,
        session=session,
        storage_dir=storage_dir,
    )

    assert first is second
    assert len(session.added) == 1
    assert session.commits == 1
    assert first.source_id == source_id
    assert first.url == origin_url
    assert first.fetched_at == fetched_at
    assert first.http_status == 200
    assert first.content_hash == "66e1b8eb7c897c53fb1180405acc82c3d562796352858bfa0d8467214f24f2d2"
    assert Path(first.storage_path).read_bytes() == b"committed fixture bytes"
    assert Path(first.storage_path).parent == storage_dir


def test_live_fetch_refuses_placeholder_contact_before_network_access(tmp_path: Path) -> None:
    with pytest.raises(HttpConfigurationError, match="contact_address"):
        fetch(
            url="https://example.gov.in/document.pdf",
            source_id=uuid4(),
            session=FakeSession(),
            storage_dir=tmp_path,
        )
