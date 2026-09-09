"""Polite HTTP collection and immutable raw-document persistence."""

from __future__ import annotations

import hashlib
import threading
import time
import tomllib
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Protocol, Self
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from uuid import UUID

from sqlmodel import Session, select

from src.core.models import RawDoc

PROJECT_NAME = "india-sourcing"
PROJECT_VERSION = "0.1"
PLACEHOLDER_CONTACT_ADDRESS = "SET_ME@example.invalid"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "http.toml"
DEFAULT_STORAGE_DIR = Path("data/raw_docs")


class FetchError(RuntimeError):
    """Raised when a URL cannot be fetched successfully."""


class RobotsDeniedError(FetchError):
    """Raised when robots.txt disallows the requested URL."""


class HttpConfigurationError(FetchError):
    """Raised when HTTP identity or policy configuration is unsafe."""


@dataclass(frozen=True, slots=True)
class HttpConfig:
    """HTTP policy loaded from ``config/http.toml``."""

    contact_address: str
    timeout_seconds: float
    max_attempts: int
    backoff_initial_seconds: float
    minimum_interval_seconds: float

    @property
    def user_agent(self) -> str:
        return f"{PROJECT_NAME}/{PROJECT_VERSION} (+{self.contact_address})"


class Response(Protocol):
    status: int

    def read(self) -> bytes: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...


Transport = Callable[[Request, float], Response]
Clock = Callable[[], float]
Sleep = Callable[[float], None]
Now = Callable[[], datetime]


class DomainRateLimiter:
    """Serialize requests so each domain sees at most one per interval."""

    def __init__(
        self,
        minimum_interval_seconds: float = 2.0,
        *,
        clock: Clock = time.monotonic,
        sleep: Sleep = time.sleep,
    ) -> None:
        if minimum_interval_seconds < 0:
            raise ValueError("minimum_interval_seconds cannot be negative")
        self.minimum_interval_seconds = minimum_interval_seconds
        self._clock = clock
        self._sleep = sleep
        self._last_request_by_domain: dict[str, float] = {}
        self._domain_locks: dict[str, threading.Lock] = {}
        self._domain_locks_lock = threading.Lock()

    def wait(self, url: str) -> None:
        domain = urlsplit(url).netloc.casefold()
        if not domain:
            raise FetchError(f"URL has no domain: {url!r}")

        with self._domain_locks_lock:
            domain_lock = self._domain_locks.setdefault(domain, threading.Lock())

        with domain_lock:
            now = self._clock()
            last_request = self._last_request_by_domain.get(domain)
            if last_request is not None:
                remaining = self.minimum_interval_seconds - (now - last_request)
                if remaining > 0:
                    self._sleep(remaining)
            self._last_request_by_domain[domain] = self._clock()


_shared_limiters: dict[float, DomainRateLimiter] = {}
_shared_limiters_lock = threading.Lock()
_shared_robots_cache: dict[str, RobotFileParser] = {}


def load_http_config(path: Path = DEFAULT_CONFIG_PATH) -> HttpConfig:
    """Load and validate HTTP policy without exposing the configured identity."""

    with path.open("rb") as config_file:
        values = tomllib.load(config_file).get("http", {})

    try:
        config = HttpConfig(
            contact_address=str(values["contact_address"]).strip(),
            timeout_seconds=float(values["timeout_seconds"]),
            max_attempts=int(values["max_attempts"]),
            backoff_initial_seconds=float(values["backoff_initial_seconds"]),
            minimum_interval_seconds=float(values["minimum_interval_seconds"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HttpConfigurationError(f"Invalid HTTP configuration in {path}") from exc

    if config.timeout_seconds <= 0:
        raise HttpConfigurationError("http.timeout_seconds must be positive")
    if config.max_attempts < 1:
        raise HttpConfigurationError("http.max_attempts must be at least 1")
    if config.backoff_initial_seconds < 0:
        raise HttpConfigurationError("http.backoff_initial_seconds cannot be negative")
    if config.minimum_interval_seconds < 2.0:
        raise HttpConfigurationError("http.minimum_interval_seconds cannot be less than 2")
    return config


def _validate_live_identity(config: HttpConfig) -> None:
    contact = config.contact_address
    if not contact or contact.casefold() == PLACEHOLDER_CONTACT_ADDRESS.casefold():
        raise HttpConfigurationError(
            "Live fetch disabled: set http.contact_address in config/http.toml "
            "to a real project contact address"
        )
    if "\r" in contact or "\n" in contact:
        raise HttpConfigurationError("http.contact_address cannot contain newlines")


def _default_transport(request: Request, timeout: float) -> Response:
    return urlopen(request, timeout=timeout)


def _shared_limiter(interval: float) -> DomainRateLimiter:
    with _shared_limiters_lock:
        return _shared_limiters.setdefault(interval, DomainRateLimiter(interval))


def _request_once(transport: Transport, request: Request, timeout: float) -> tuple[int, bytes]:
    try:
        with transport(request, timeout) as response:
            return response.status, response.read()
    except HTTPError as exc:
        body = exc.read()
        return exc.code, body


def _request_with_retries(
    *,
    url: str,
    transport: Transport,
    config: HttpConfig,
    limiter: DomainRateLimiter,
    sleep: Sleep,
) -> tuple[int, bytes]:
    request = Request(url, headers={"User-Agent": config.user_agent})
    for attempt in range(config.max_attempts):
        limiter.wait(url)
        try:
            status, content = _request_once(transport, request, config.timeout_seconds)
        except (OSError, TimeoutError, URLError) as exc:
            if attempt + 1 == config.max_attempts:
                raise FetchError(
                    f"Fetch failed for {url} after {config.max_attempts} attempts"
                ) from exc
        else:
            if status < 500:
                return status, content
            if attempt + 1 == config.max_attempts:
                raise FetchError(f"Fetch failed for {url} with HTTP status {status}")

        sleep(config.backoff_initial_seconds * (2**attempt))

    raise AssertionError("retry loop exited unexpectedly")


def _robots_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise FetchError(f"Unsupported fetch URL: {url!r}")
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def _robots_policy(
    *,
    url: str,
    transport: Transport,
    config: HttpConfig,
    limiter: DomainRateLimiter,
    sleep: Sleep,
    cache: MutableMapping[str, RobotFileParser],
) -> RobotFileParser:
    robots_url = _robots_url(url)
    cached = cache.get(robots_url)
    if cached is not None:
        return cached

    status, content = _request_with_retries(
        url=robots_url,
        transport=transport,
        config=config,
        limiter=limiter,
        sleep=sleep,
    )
    parser = RobotFileParser(robots_url)
    if status == 200:
        parser.parse(content.decode("utf-8", errors="replace").splitlines())
    elif status in {401, 403}:
        parser.parse(["User-agent: *", "Disallow: /"])
    elif 400 <= status < 500:
        parser.parse(["User-agent: *", "Allow: /"])
    else:
        raise FetchError(f"Unable to check robots.txt at {robots_url}: HTTP status {status}")
    cache[robots_url] = parser
    return parser


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _write_content_once(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as output:
            output.write(content)
    except FileExistsError:
        if path.read_bytes() != content:
            raise FetchError(f"Content-addressed path contains unexpected bytes: {path}") from None


def fetch(
    *,
    url: str,
    source_id: UUID,
    session: Session,
    storage_dir: Path = DEFAULT_STORAGE_DIR,
    transport: Transport | None = None,
    clock: Clock = time.monotonic,
    sleep: Sleep = time.sleep,
    now: Now = _utc_now,
    limiter: DomainRateLimiter | None = None,
    robots_cache: MutableMapping[str, RobotFileParser] | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> RawDoc:
    """Fetch a URL politely, persist its bytes once, and return its immutable row."""

    config = load_http_config(config_path)
    if transport is None:
        _validate_live_identity(config)
        transport = _default_transport

    if limiter is not None:
        active_limiter = limiter
    elif clock is time.monotonic and sleep is time.sleep:
        active_limiter = _shared_limiter(config.minimum_interval_seconds)
    else:
        active_limiter = DomainRateLimiter(
            config.minimum_interval_seconds,
            clock=clock,
            sleep=sleep,
        )
    active_robots_cache = robots_cache if robots_cache is not None else _shared_robots_cache
    robots = _robots_policy(
        url=url,
        transport=transport,
        config=config,
        limiter=active_limiter,
        sleep=sleep,
        cache=active_robots_cache,
    )
    if not robots.can_fetch(PROJECT_NAME, url):
        raise RobotsDeniedError(f"robots.txt disallows fetching {url}")

    status, content = _request_with_retries(
        url=url,
        transport=transport,
        config=config,
        limiter=active_limiter,
        sleep=sleep,
    )
    if not 200 <= status < 300:
        raise FetchError(f"Fetch failed for {url} with HTTP status {status}")

    content_hash = hashlib.sha256(content).hexdigest()
    existing = session.exec(select(RawDoc).where(RawDoc.content_hash == content_hash)).first()
    if existing is not None:
        return existing

    storage_path = storage_dir / content_hash
    _write_content_once(storage_path, content)
    raw_doc = RawDoc(
        source_id=source_id,
        url=url,
        fetched_at=now(),
        content_hash=content_hash,
        storage_path=str(storage_path),
        http_status=status,
    )
    session.add(raw_doc)
    session.commit()
    session.refresh(raw_doc)
    return raw_doc
