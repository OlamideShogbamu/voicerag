# VoiceRAG

Real-time voice assistant with personal RAG knowledge.

Speak to it. It answers. Say "remember that…" and it stores the note in
pgvector so it can recall it the next time you ask.

## Stack

- **frontend** — Next.js + LiveKit client (`apps/frontend`)
- **backend**  — FastAPI: LiveKit token + ingest endpoints (`apps/backend`)
- **agents**   — LiveKit Python worker: STT → LLM → TTS, with `search_knowledge` and `save_knowledge` tools (`apps/agents`)
- **db**       — PostgreSQL with pgvector

## Quick start

```bash
make bootstrap     # install pnpm + uv deps, copy env files
make docker-up     # start Postgres+pgvector
make dev-backend   # FastAPI on :8000
make dev-agents    # LiveKit worker
make dev-frontend  # Next.js on :3000
```

Open `http://localhost:3000`, tap the orb, talk.

## Environment

Each app reads its own `.env`. The required keys:

- `DATABASE_URL` — postgres connection string (backend, agents)
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` (backend, agents)
- `OPENAI_API_KEY` (backend, agents)
- `DEEPGRAM_API_KEY` (agents)
- `NEXT_PUBLIC_API_URL` (frontend, default `http://localhost:8000`)

## Schema

Single migration: `apps/backend/app/db/migrations/001_initial.sql`. One
table — `public.embeddings` — keyed by `user_id` (any string, the
frontend issues a UUID per browser).
