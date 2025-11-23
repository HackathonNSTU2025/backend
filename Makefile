.SILENT:

up:
	docker compose -f ./deploy/docker-compose.yml up --build -d
	docker compose -f ./deploy/docker-compose.yml logs -f app

down:
	docker compose -f ./deploy/docker-compose.yml down

lint:
	uvx ruff check ./app/

update:
	uv sync -U
	uv pip compile pyproject.toml > requirements.txt
