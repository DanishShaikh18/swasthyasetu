"""Storage service — Supabase file upload with presigned URLs."""

import logging

from app.config import settings

logger = logging.getLogger(__name__)

_supabase_client = None
try:
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        from supabase import create_client
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase Storage initialized")
    else:
        logger.warning("Supabase credentials not set — file uploads will use local fallback")
except Exception as e:
    logger.warning(f"Supabase init failed: {e}")


async def get_upload_url(bucket: str, path: str) -> dict:
    """Get a presigned upload URL from Supabase Storage."""
    if not _supabase_client:
        # Return a mock URL for development
        return {
            "upload_url": f"/api/v1/uploads/mock/{path}",
            "public_url": f"/uploads/{path}",
            "message": "Supabase not configured — using mock URLs",
        }
    try:
        result = _supabase_client.storage.from_(bucket).create_signed_upload_url(path)
        public_url = _supabase_client.storage.from_(bucket).get_public_url(path)
        return {
            "upload_url": result.get("signedURL", ""),
            "public_url": public_url,
        }
    except Exception as e:
        logger.error(f"Supabase upload URL error: {e}")
        return {"upload_url": "", "public_url": "", "error": str(e)}


async def delete_file(bucket: str, path: str) -> bool:
    """Delete a file from Supabase Storage."""
    if not _supabase_client:
        return True
    try:
        _supabase_client.storage.from_(bucket).remove([path])
        return True
    except Exception as e:
        logger.error(f"Supabase delete error: {e}")
        return False
