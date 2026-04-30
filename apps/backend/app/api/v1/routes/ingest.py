"""
/ingest — knowledge ingestion endpoints for the VoiceRAG knowledge base.

POST /ingest/text  — embed a free-form note for RAG retrieval
POST /ingest/audio — transcribe an audio clip and embed the transcript
"""

from __future__ import annotations

import os

import asyncpg
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.db.session import get_pool
from app.services.ingest.embedder import store_embedding
from app.services.ingest.voicemaker import transcribe_audio

router = APIRouter()

_AUDIO_SIZE_LIMIT = 50 * 1024 * 1024  # 50 MB
_AUDIO_EXTENSIONS = {
    ".mp3", ".mp4", ".wav", ".ogg", ".webm",
    ".m4a", ".flac", ".aac", ".opus", ".mkv", ".mov",
}


class TextNoteRequest(BaseModel):
    user_id: str
    content: str
    source_ref: str | None = None


@router.post("/text")
async def ingest_text(
    body: TextNoteRequest,
    pool: asyncpg.Pool = Depends(get_pool),
):
    """Embed and store a free-form note for later RAG retrieval."""
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    if len(body.content) > 8000:
        raise HTTPException(status_code=400, detail="Content too long (max 8000 chars)")

    embedding_id = await store_embedding(
        pool,
        body.user_id,
        body.content.strip(),
        source_type="text",
        source_ref=body.source_ref,
    )
    return {"id": embedding_id, "stored": True}


@router.post("/audio")
async def ingest_audio(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    language: str = Form(default="auto"),
    pool: asyncpg.Pool = Depends(get_pool),
):
    """Upload audio, transcribe with VoiceMaker, embed the transcript."""
    api_key = os.getenv("VOICEMAKER_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="Audio transcription not configured")

    filename = file.filename or "upload"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in _AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Accepted: {', '.join(sorted(_AUDIO_EXTENSIONS))}",
        )

    data = await file.read()
    if len(data) > _AUDIO_SIZE_LIMIT:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    try:
        transcript = await transcribe_audio(
            data=data,
            filename=filename,
            mime_type=file.content_type or "application/octet-stream",
            api_key=api_key,
            language=language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    embedding_id = await store_embedding(
        pool,
        user_id,
        transcript,
        source_type="audio_transcript",
        source_ref=filename,
        metadata={"language_requested": language, "filename": filename},
    )

    return {"transcript": transcript, "id": embedding_id, "stored": True}
