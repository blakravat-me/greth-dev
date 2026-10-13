ENV_FILE := $(if $(wildcard .env),--env-file .env,)

.PHONY: install run test lint format check

install:
	uv sync

run:
	uv run $(ENV_FILE) python main.py

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .
	uv run ruff format .

check: lint test
