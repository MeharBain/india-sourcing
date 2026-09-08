"""Global pytest configuration that disables network access for every test."""

import pytest


@pytest.fixture(autouse=True)
def _disable_network(socket_disabled: object) -> None:
    """Require every test to run with sockets disabled by pytest-socket."""
