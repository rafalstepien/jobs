run-linters:
	ruff check --fix
	ruff format


generate:
	python3 src/cli.py generate