# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV UV_LINK_MODE=copy \
    UV_PYTHON=python3.12 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "python", "-m", "agent.worker", "start"]
