"""Auth service — JWT tokens, password hashing, Redis session management."""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.dependencies import get_redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, role: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "user_id": user_id,
        "role": role,
        "email": email,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "user_id": user_id,
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def store_refresh_token(user_id: str, token: str):
    """Store refresh token hash in Redis."""
    redis_client = await get_redis()
    if not redis_client:
        return
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    await redis_client.setex(f"refresh:{user_id}:{token_hash}", ttl, "1")


async def verify_refresh_token(user_id: str, token: str) -> bool:
    """Verify refresh token exists in Redis."""
    redis_client = await get_redis()
    if not redis_client:
        return True  # Graceful fallback
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await redis_client.get(f"refresh:{user_id}:{token_hash}")
    return result is not None


async def revoke_refresh_token(user_id: str, token: str):
    """Delete refresh token from Redis."""
    redis_client = await get_redis()
    if not redis_client:
        return
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    await redis_client.delete(f"refresh:{user_id}:{token_hash}")


async def blocklist_access_token(token: str, ttl_seconds: int = 900):
    """Add access token to blocklist in Redis."""
    redis_client = await get_redis()
    if not redis_client:
        return
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    await redis_client.setex(f"token_blocklist:{token_hash}", ttl_seconds, "1")
