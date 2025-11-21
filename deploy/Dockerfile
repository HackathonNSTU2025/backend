FROM ghcr.io/astral-sh/uv:python3.13-alpine

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --compile-bytecode && \
    source ./.venv/bin/activate

EXPOSE 8000

COPY ./app/ ./app/

ENTRYPOINT ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
