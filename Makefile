.PHONY: install test coverage lint typecheck check

install:
	uv sync --extra dev

test:
	uv run pytest

coverage:
	uv run pytest --cov --cov-report=term-missing

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

check: lint typecheck coverage
