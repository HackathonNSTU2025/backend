.SILENT:

run:
	uvicorn app.main:app --reload --port 8000

lint:
	uvx ruff check

update:
	uv sync -U
	uv pip compile pyproject.toml > requirements.txt
