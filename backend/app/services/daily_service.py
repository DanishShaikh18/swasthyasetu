"""Daily.co video service — room creation and token generation."""

import time
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DAILY_API_BASE = "https://api.daily.co/v1"


def _get_headers() -> dict:
    return {"Authorization": f"Bearer {settings.DAILY_API_KEY}"}


async def create_room(room_name: str) -> dict | None:
    """Create a Daily.co room. Returns room info or None on failure."""
    if not settings.DAILY_API_KEY:
        logger.warning("DAILY_API_KEY not set — returning mock room")
        return {
            "name": room_name,
            "url": f"https://your-domain.daily.co/{room_name}",
            "id": "mock-room-id",
        }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DAILY_API_BASE}/rooms",
                headers=_get_headers(),
                json={
                    "name": room_name,
                    "properties": {
                        "exp": int(time.time()) + 7200,
                        "enable_chat": True,
                        "enable_screenshare": False,
                        "max_participants": 2,
                    },
                },
                timeout=10.0,
            )
            if response.status_code == 200:
                return response.json()
            # Room may already exist
            if response.status_code == 400:
                get_resp = await client.get(
                    f"{DAILY_API_BASE}/rooms/{room_name}",
                    headers=_get_headers(),
                    timeout=10.0,
                )
                if get_resp.status_code == 200:
                    return get_resp.json()
            logger.error(f"Daily room creation failed: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Daily API error: {e}")
        return None


async def create_meeting_token(
    room_name: str, is_owner: bool = False
) -> str | None:
    """Create a meeting token (2hr expiry). NEVER store this in DB."""
    if not settings.DAILY_API_KEY:
        logger.warning("DAILY_API_KEY not set — returning mock token")
        return "mock-daily-token-for-development"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DAILY_API_BASE}/meeting-tokens",
                headers=_get_headers(),
                json={
                    "properties": {
                        "room_name": room_name,
                        "is_owner": is_owner,
                        "exp": int(time.time()) + 7200,
                    }
                },
                timeout=10.0,
            )
            if response.status_code == 200:
                return response.json()["token"]
            logger.error(f"Daily token creation failed: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Daily API error: {e}")
        return None
