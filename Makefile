.PHONY: install test lint eval serve

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	python -m ruff check .

eval:
	llm-reliability-eval sample_data/eval_cases.jsonl --json reports/report.json --html reports/report.html

serve:
	uvicorn llm_reliability_lab.api:app --reload
