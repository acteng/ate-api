bin = .venv/bin
packages = ate_api tests

black-check:
	$(bin)/black --check $(packages)

isort-check:
	$(bin)/isort --check-only $(packages)

format-check: black-check isort-check

black:
	$(bin)/black $(packages)

isort:
	$(bin)/isort $(packages)

format: black isort

mypy:
	$(bin)/mypy $(packages)

ruff:
	$(bin)/ruff check $(packages)

lint: mypy ruff

ruff-fix:
	$(bin)/ruff check --fix $(packages)

fix: ruff-fix

test:
	$(bin)/pytest

verify: format-check lint test

run:
	$(bin)/fastapi dev ate_api/main.py
