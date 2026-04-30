FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install C build tools needed by webrtcvad (pulled in by resemblyzer)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev deps)
RUN uv sync --frozen --no-dev

# Copy agent source
COPY agent/ ./agent/

# Pre-download Silero VAD model at build time (not at runtime)
RUN uv run python -c "from livekit.plugins import silero; silero.VAD.load()"

CMD ["uv", "run", "python", "-m", "agent.worker", "start"]
