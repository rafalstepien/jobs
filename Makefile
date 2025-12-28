run-linters:
	ruff format
	ruff check --fix
	mypy .


report:
	python3 src/cli.py generate