.PHONY: install dev lint format typecheck test clean run build preprocess

install:
	pip install -e ".[dev]"

dev:
	pip install -e ".[dev]"

lint:
	ruff check .

format:
	black .

typecheck:
	cd .. && mypy -p backend --disable-error-code=import-untyped --disable-error-code=import-not-found

test:
	pytest tests/ -v

build: lint format typecheck test

run:
	uvicorn main:app --reload --port 8000

preprocess:
	python scripts/preprocess.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache/ .ruff_cache/ .pytest_cache/ .coverage htmlcov/
