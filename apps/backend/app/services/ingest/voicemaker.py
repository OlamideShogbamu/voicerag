"""
VoiceMaker ASR client — async transcription via api.myvoicemaker.ai.

Usage:
    transcript = await transcribe_audio(file_bytes, filename, mime_type)
"""

from __future__ import annotations

import asyncio

import httpx

_BASE_URL = "http://api.myvoicemaker.ai/api/developer/v1"
_POLL_INTERVAL = 3          # seconds between status checks
_TIMEOUT_SECONDS = 300      # 5-minute hard ceiling


async def transcribe_audio(
    data: bytes,
    filename: str,
    mime_type: str,
    api_key: str,
    language: str = "auto",
    timestamp_level: str = "none",
    diarization_mode: str = "off",
) -> str:
    """
    Submit an audio/video file to VoiceMaker, poll until complete, and
    return the transcript text.

    Raises:
        ValueError  — transcription failed or timed out.
        httpx.HTTPStatusError — non-2xx response from the API.
    """
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Submit the job
        resp = await client.post(
            f"{_BASE_URL}/transcriptions",
            headers=headers,
            files={"file": (filename, data, mime_type)},
            data={
                "languageRequested": language,
                "timestampLevel": timestamp_level,
                "diarizationMode": diarization_mode,
            },
        )
        resp.raise_for_status()

        job_id: str = resp.json()["id"]

        # 2. Poll until terminal state
        elapsed = 0
        while elapsed < _TIMEOUT_SECONDS:
            await asyncio.sleep(_POLL_INTERVAL)
            elapsed += _POLL_INTERVAL

            poll = await client.get(
                f"{_BASE_URL}/transcriptions/{job_id}",
                headers=headers,
            )
            poll.raise_for_status()
            job = poll.json()

            status = job.get("status")
            if status == "COMPLETED":
                transcript = job.get("transcriptText") or ""
                if not transcript:
                    raise ValueError("Transcription completed but returned empty text.")
                return transcript

            if status == "FAILED":
                msg = job.get("errorMessage") or "Unknown error"
                raise ValueError(f"VoiceMaker transcription failed: {msg}")

        raise ValueError("Transcription timed out after 5 minutes.")
