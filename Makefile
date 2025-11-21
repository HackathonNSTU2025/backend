.SILENT:

up:
	docker compose -f ./deploy/docker-compose.yml up --build

down:
	docker compose -f ./deploy/docker-compose.yml down

lint:
	uvx ruff check

update:
	uv sync -U
	uv pip compile pyproject.toml > requirements.txt
