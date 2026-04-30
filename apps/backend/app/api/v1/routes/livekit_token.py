import logging
import uuid

from fastapi import APIRouter
from livekit.api import (
    AccessToken,
    CreateRoomRequest,
    LiveKitAPI,
    VideoGrants,
)
from livekit.protocol.agent_dispatch import CreateAgentDispatchRequest
from livekit.protocol.models import ParticipantInfo
from livekit.protocol.room import ListParticipantsRequest

from app.core.config import settings

router = APIRouter()
log = logging.getLogger(__name__)


def _public_url() -> str:
    return settings.livekit_public_url or settings.livekit_url


@router.get("/token")
async def get_livekit_token(user_id: str | None = None):
    """Issue a LiveKit token and dispatch the VoiceRAG agent.

    Pass ?user_id=<uuid> to scope embeddings to a returning visitor;
    omit it for a fresh guest identity.
    """
    identity = user_id or f"guest-{uuid.uuid4().hex[:12]}"
    room_name = f"voicerag-{identity}"
    print(f"[token] identity={identity} room={room_name}", flush=True)

    token = (
        AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )

    async with LiveKitAPI(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    ) as lkapi:
        await lkapi.room.create_room(
            CreateRoomRequest(
                name=room_name,
                empty_timeout=300,
                departure_timeout=90,
            )
        )
        resp = await lkapi.room.list_participants(ListParticipantsRequest(room=room_name))
        agent_present = any(p.kind == ParticipantInfo.Kind.AGENT for p in resp.participants)
        log.info("room=%s participants=%d agent_present=%s", room_name, len(resp.participants), agent_present)
        if not agent_present:
            dispatch = await lkapi.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(agent_name="voicerag", room=room_name)
            )
            log.info("dispatch created id=%s room=%s", dispatch.id, room_name)
        else:
            log.info("agent already in room — skipping dispatch room=%s", room_name)

    return {
        "token": token,
        "room_name": room_name,
        "server_url": _public_url(),
        "identity": identity,
    }
