"""Notification service — FCM push + in-app database notifications."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.notification import Notification

logger = logging.getLogger(__name__)

# Try to initialize Firebase
_firebase_initialized = False
try:
    if settings.FIREBASE_CREDENTIALS:
        import firebase_admin
        from firebase_admin import credentials, messaging
        import json, os
        creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if creds_json:
            cred = credentials.Certificate(json.loads(creds_json))
        else:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase initialized successfully")
    else:
        logger.warning("FIREBASE_CREDENTIALS not set — push notifications disabled")
except Exception as e:
    logger.warning(f"Firebase init failed: {e} — push notifications disabled")


async def send_push(fcm_token: str, title: str, body: str, data: dict = None):
    """Send push via FCM. Silently fails if Firebase unavailable."""
    if not _firebase_initialized or not fcm_token:
        return
    try:
        from firebase_admin import messaging
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=fcm_token,
        )
        messaging.send(message)
    except Exception as e:
        logger.error(f"FCM push failed: {e}")


async def send(
    db: AsyncSession,
    user_id: UUID,
    type: str,
    title: str,
    body: str,
    data: dict = None,
    fcm_token: str = None,
):
    """Create in-app notification + send push if FCM token available."""
    try:
        notif = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            data=data or {},
        )
        db.add(notif)
        await db.flush()

        if fcm_token:
            await send_push(fcm_token, title, body, data)
    except Exception as e:
        logger.error(f"Notification send failed: {e}")
