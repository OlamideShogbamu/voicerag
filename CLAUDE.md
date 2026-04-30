# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Monorepo

```
apps/
  frontend/   Next.js 16 — single voice-console page
  backend/    FastAPI    — LiveKit token + RAG ingest
  agents/     Python     — LiveKit voice worker, STT → LLM → TTS
infra/        Docker compose, Dockerfiles
```

JS managed by pnpm + Turborepo, Python by uv.

## Commands

```bash
make bootstrap      # install all deps, copy envs
make docker-up      # postgres+pgvector
make dev-backend    # FastAPI :8000
make dev-agents     # LiveKit worker
make dev-frontend   # Next.js :3000

# Migrations (single file): owner is postgres OS user
sudo -u postgres psql voicerag -c "$(cat apps/backend/app/db/migrations/001_initial.sql)"

# Tests
cd apps/backend && uv run pytest
cd apps/agents  && uv run pytest
```

## Architecture

### `apps/frontend`
- App Router, Tailwind v4, shadcn/ui, LiveKit client.
- One route — `/dashboard/console` — connects to LiveKit and renders the orb.
- `lib/api-client.ts` issues a per-browser UUID stored in `localStorage`
  (`voicerag_user_id`) so embeddings are scoped per visitor without auth.

### `apps/backend` (FastAPI)
- `GET /livekit/token?user_id=<uuid>` — issues a LiveKit token and dispatches
  the `voicerag` agent into the room.
- `POST /ingest/text` — embeds free-form text into `public.embeddings`.
- `POST /ingest/audio` — transcribes (VoiceMaker) then embeds.
- No auth. `user_id` flows in from the request.

### `apps/agents` (LiveKit Python worker)
- Single agent: `VoiceRAGAgent`.
- Tools: `search_knowledge` (top-k cosine over pgvector) and `save_knowledge`
  (embed + insert). System prompt in `agent/prompts/voicerag.py`.
- Pipeline: Deepgram STT → OpenAI GPT-4.1-mini → Edge TTS, Silero VAD.
- Participant identity = `user_id` (set by backend token endpoint).

## Data model

Single table — `public.embeddings(id, user_id, source_type, source_ref,
content, embedding vector(512), metadata jsonb, created_at)`.

`source_type` is one of `text | audio_transcript | voice_note`.

## Frontend conventions
- TypeScript strict, no `any`.
- Named exports only (Next.js pages excepted).
- Components stay dumb; logic lives in custom hooks.
- Tailwind only — no inline styles.
- `kebab-case` filenames.
