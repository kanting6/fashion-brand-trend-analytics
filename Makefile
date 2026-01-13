SHELL := /bin/bash
.PHONY: demo demo-sample test lint clean

demo:
	python -m fashion_trends demo

demo-sample:
	RAW_DIR=data/sample python -m fashion_trends demo-existing

test:
	pytest -q

lint:
	ruff check .
	ruff format --check .

clean:
	rm -rf warehouse exports/tableau data/raw .pytest_cache __pycache__
