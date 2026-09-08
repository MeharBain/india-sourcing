.PHONY: test lint run

test:
	uv run pytest

lint:
	uv run ruff check .

run:
	uv run python -m src.surfaces.app
