"""Content router — daily tips, first aid, health facts with Redis caching."""

import hashlib
import json
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.notification import HealthContent, Notification
from app.models.user import User
from app.dependencies import get_current_user, get_redis, get_optional_user

router = APIRouter(tags=["Content"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


async def _get_cached(key: str):
    redis = await get_redis()
    if redis:
        cached = await redis.get(key)
        if cached:
            return json.loads(cached)
    return None


async def _set_cached(key: str, data, ttl: int):
    redis = await get_redis()
    if redis:
        await redis.setex(key, ttl, json.dumps(data))


@router.get("/daily-tip")
async def get_daily_tip(
    language: str = Query("hi"),
    state: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get daily tip — cached 24 hours."""
    today = date.today().isoformat()
    cache_key = f"daily_tip:{language}:{state or 'national'}:{today}"

    cached = await _get_cached(cache_key)
    if cached:
        return _success(cached, "cached")

    query = select(HealthContent).where(
        HealthContent.type == "daily_tip",
        HealthContent.language == language,
    )
    if state:
        query = query.where(
            (HealthContent.state == state) | (HealthContent.state.is_(None))
        )
    query = query.order_by(func.random()).limit(1)

    result = await db.execute(query)
    tip = result.scalar_one_or_none()

    if not tip:
        # Fallback: try English
        result = await db.execute(
            select(HealthContent)
            .where(HealthContent.type == "daily_tip", HealthContent.language == "en")
            .order_by(func.random()).limit(1)
        )
        tip = result.scalar_one_or_none()

    if not tip:
        data = {
            "title": "Stay Healthy!",
            "body": "Drink 8 glasses of water daily and eat fresh vegetables.",
            "language": language,
        }
    else:
        data = {
            "id": str(tip.id),
            "title": tip.title,
            "body": tip.body,
            "language": tip.language,
            "state": tip.state,
        }

    await _set_cached(cache_key, data, 86400)
    return _success(data)


@router.get("/first-aid")
async def get_first_aid(
    language: str = Query("hi"),
    category: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get first aid cards — cached 7 days."""
    cache_key = f"first_aid:{language}:{category or 'all'}"

    cached = await _get_cached(cache_key)
    if cached:
        return _success(cached, "cached")

    query = select(HealthContent).where(
        HealthContent.type == "first_aid",
        HealthContent.language == language,
    )
    if category:
        query = query.where(HealthContent.title.ilike(f"%{category}%"))

    result = await db.execute(query)
    cards = result.scalars().all()

    data = [{
        "id": str(c.id),
        "title": c.title,
        "body": c.body,
        "language": c.language,
    } for c in cards]

    if not data:
        # Try English fallback
        result = await db.execute(
            select(HealthContent).where(
                HealthContent.type == "first_aid", HealthContent.language == "en"
            )
        )
        cards = result.scalars().all()
        data = [{"id": str(c.id), "title": c.title, "body": c.body, "language": "en"} for c in cards]

    await _set_cached(cache_key, data, 604800)
    return _success(data)


@router.get("/health-facts")
async def get_health_facts(
    language: str = Query("hi"),
    db: AsyncSession = Depends(get_db),
):
    """Get health facts — cached 6 hours."""
    cache_key = f"health_facts:{language}"

    cached = await _get_cached(cache_key)
    if cached:
        return _success(cached, "cached")

    result = await db.execute(
        select(HealthContent).where(
            HealthContent.type.in_(["nutrition", "seasonal_alert"]),
            HealthContent.language == language,
        ).limit(20)
    )
    facts = result.scalars().all()

    data = [{
        "id": str(f.id),
        "type": f.type,
        "title": f.title,
        "body": f.body,
        "season": f.season,
        "state": f.state,
    } for f in facts]

    await _set_cached(cache_key, data, 21600)
    return _success(data)


# Notification endpoints (shared)
@router.get("/notifications/me")
async def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * limit).limit(limit)
    )
    notifications = result.scalars().all()
    return _success([{
        "id": str(n.id),
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "data": n.data,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
    } for n in notifications])


@router.patch("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import uuid as _uuid
    result = await db.execute(
        select(Notification).where(
            Notification.id == _uuid.UUID(notification_id),
            Notification.user_id == user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    return _success(None, "Marked as read")
