run-linters:
	ruff check --fix
	ruff format


report:
	python3 src/cli.py generate