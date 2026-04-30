# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

WORKDIR /app

# System deps in a single cached layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN pip install --no-cache-dir uv

# 1. Copy only the dependency manifest first.
#    This layer is cached as long as pyproject.toml / uv.lock don't change.
COPY pyproject.toml uv.lock ./

# 2. Install deps — uv cache persists via BuildKit across builds.
#    --compile-bytecode pre-compiles .pyc files for faster cold starts.
#    --no-dev skips test/lint deps.
RUN --mount=type=cache,id=uv-cache-backend,target=/root/.cache/uv \
    uv sync --frozen --no-dev --compile-bytecode

# 3. Copy source — only re-runs when app code changes.
COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
