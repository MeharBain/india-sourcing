"""Source-specific discovery and parsing adapters."""

from src.connectors.base import Connector, FetchTarget, discover_connectors

REGISTERED_CONNECTORS = discover_connectors()

__all__ = ["REGISTERED_CONNECTORS", "Connector", "FetchTarget", "discover_connectors"]
