"""Structural smoke tests for the repository scaffold."""

from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "src.core.models",
        "src.core.provenance",
        "src.core.storage",
        "src.connectors.base",
        "src.extract.deterministic",
        "src.extract.llm",
        "src.resolve.normalize",
        "src.resolve.blocking",
        "src.resolve.features",
        "src.resolve.decide",
        "src.enrich",
        "src.score.compute",
        "src.surfaces.digest",
        "src.surfaces.app",
    ],
)
def test_scaffold_module_is_importable(module_name: str) -> None:
    """Keep every declared pipeline module importable while it is empty."""
    import_module(module_name)
