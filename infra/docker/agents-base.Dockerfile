# syntax=docker/dockerfile:1.7
# Pre-built base image containing all heavy dependencies for the agents service.
# Build and push this ONLY when pyproject.toml / uv.lock changes:
#
#   gcloud builds submit . \
#     --config=apps/agents/cloudbuild-base.yaml \
#     --project=voice-miner-equalyz
#
# The agents.Dockerfile FROM line points to this image so normal code-change
# builds skip all dependency installation entirely (~30s instead of 18min).

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY apps/agents/pyproject.toml apps/agents/uv.lock ./

RUN --mount=type=cache,id=uv-cache-agents,target=/root/.cache/uv \
    uv sync --frozen --no-dev --compile-bytecode
