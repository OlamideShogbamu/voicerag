-- VoiceRAG schema — minimal, single-table RAG store backed by pgvector.
-- Apply with: sudo -u postgres psql voicerag -c "$(cat 001_initial.sql)"
-- Requires:   sudo apt-get install postgresql-16-pgvector

SET client_encoding = 'UTF8';

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS vector   WITH SCHEMA public;

-- ─── public.embeddings ────────────────────────────────────────────────────────
-- One row per stored knowledge chunk.  user_id is just a free-form string
-- (any UUID or guest identity) so the agent can scope retrieval per visitor
-- without a separate users table.

CREATE TABLE public.embeddings (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     TEXT NOT NULL,
    source_type VARCHAR(30) NOT NULL,
    -- 'text' | 'audio_transcript' | 'voice_note'
    source_ref  TEXT,
    content     TEXT NOT NULL,
    embedding   vector(512),
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX embeddings_user_cosine_idx
    ON public.embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 50);

CREATE INDEX embeddings_user_type_idx
    ON public.embeddings (user_id, source_type, created_at DESC);

-- ─── Role grant ───────────────────────────────────────────────────────────────

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'voicerag') THEN
        CREATE ROLE voicerag WITH LOGIN PASSWORD 'voicerag';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO voicerag;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.embeddings TO voicerag;
