from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import close_pool, create_pool
from app.api.v1.routes import ingest, livekit_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    yield
    await close_pool()


app = FastAPI(title="VoiceRAG API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(livekit_token.router, prefix="/livekit", tags=["livekit"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])


@app.get("/health")
async def health():
    return {"status": "ok"}
