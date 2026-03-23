"""FastAPI dependencies — DB sessions, auth, role guards, Redis, rate limiting."""

import uuid
import hashlib
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
import redis.asyncio as aioredis

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)

# Redis connection (lazy init)
_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create Redis connection."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = aioredis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
            await _redis_client.ping()
        except Exception:
            # Fallback: return a dummy redis that doesn't crash
            _redis_client = None
            return None
    return _redis_client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT, return the User object."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Check if token is blocklisted
    redis_client = await get_redis()
    if redis_client:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        blocked = await redis_client.get(f"token_blocklist:{token_hash}")
        if blocked:
            raise HTTPException(status_code=401, detail="Token has been revoked")

    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get user if token exists, otherwise None (for optional auth)."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_role(*roles: str):
    """Dependency factory: restrict endpoint to specific roles."""
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(roles)}"
            )
        return user
    return role_checker


def require_approved_doctor():
    """Dependency: require approved doctor."""
    async def checker(user: User = Depends(get_current_user)):
        if user.role != "doctor":
            raise HTTPException(status_code=403, detail="Doctor access required")
        from sqlalchemy import select
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            from app.models.doctor import DoctorProfile
            result = await db.execute(
                select(DoctorProfile).where(DoctorProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()
            if not profile or not profile.is_approved:
                raise HTTPException(
                    status_code=403,
                    detail="Doctor account pending approval"
                )
        return user
    return checker


async def check_rate_limit(
    key: str, max_requests: int, window_seconds: int
) -> bool:
    """Check and increment rate limit counter. Returns True if allowed."""
    redis_client = await get_redis()
    if not redis_client:
        return True  # No Redis = no rate limiting (graceful degradation)
    current = await redis_client.get(key)
    if current and int(current) >= max_requests:
        return False
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds)
    await pipe.execute()
    return True
