.PHONY: check format test generate doctor

check:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	pytest

generate:
	python scripts/generate_dev_tasks.py

doctor:
	omniwebbench doctor
