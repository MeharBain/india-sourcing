"""Define the shared connector contract and connector discovery registry."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from types import ModuleType
from typing import TypeAlias

from src.core.models import RawDoc, Signal

Cadence: TypeAlias = str


@dataclass(frozen=True, slots=True)
class FetchTarget:
    """A source document URL discovered by a connector."""

    url: str

    def __post_init__(self) -> None:
        if not self.url.strip():
            raise ValueError("FetchTarget.url cannot be empty")


class Connector(ABC):
    """Discover source documents and parse immutable snapshots into signals."""

    key: str
    cadence: Cadence

    @abstractmethod
    def discover(self) -> Iterable[FetchTarget]:
        """Yield URLs to fetch. No parsing, no network writes to DB."""

    @abstractmethod
    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        """Pure function. RawDoc in, Signals out. No network. No DB. No I/O."""

    @abstractmethod
    def contract_raw_docs(self) -> Iterable[RawDoc]:
        """Return immutable fixture documents used by cross-connector contract tests."""

    @abstractmethod
    def contract_signals(self) -> Iterable[Signal]:
        """Return signals parsed from the connector's contract fixtures."""


def _connector_classes(module: ModuleType) -> Iterable[type[Connector]]:
    for _, candidate in inspect.getmembers(module, inspect.isclass):
        if (
            candidate is not Connector
            and candidate.__module__ == module.__name__
            and issubclass(candidate, Connector)
            and not inspect.isabstract(candidate)
        ):
            yield candidate


def discover_connectors(
    package_name: str = "src.connectors",
) -> tuple[type[Connector], ...]:
    """Import connector modules and register every concrete Connector subclass."""

    package = importlib.import_module(package_name)
    modules = [package]
    if hasattr(package, "__path__"):
        for module_info in pkgutil.walk_packages(package.__path__, f"{package.__name__}."):
            if any(part.startswith("test") for part in module_info.name.split(".")):
                continue
            modules.append(importlib.import_module(module_info.name))

    registry: dict[str, type[Connector]] = {}
    for module in modules:
        for connector_class in _connector_classes(module):
            if not connector_class.key.strip():
                raise ValueError(f"{connector_class.__name__}.key cannot be empty")
            if connector_class.key in registry:
                other = registry[connector_class.key]
                raise ValueError(
                    f"Duplicate connector key {connector_class.key!r}: "
                    f"{other.__name__} and {connector_class.__name__}"
                )
            registry[connector_class.key] = connector_class

    return tuple(registry[key] for key in sorted(registry))
