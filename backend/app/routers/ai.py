"""AI router — symptom checker with rate limiting."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.patient import PatientProfile, SymptomLog
from app.schemas.ai import SymptomCheckRequest, SymptomCheckResponse
from app.dependencies import get_current_user, get_optional_user, check_rate_limit
from app.services import gemini_service

import json

router = APIRouter(tags=["AI"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


@router.post("/symptoms")
async def check_symptoms(
    req: SymptomCheckRequest,
    request: Request,
    user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """AI symptom checker — rate limited to 5 per user per hour."""
    # Use user ID for authenticated users, client IP for anonymous
    if user:
        rate_identity = str(user.id)
    else:
        rate_identity = request.client.host if request.client else "unknown"
    rate_key = f"rate_limit:symptoms:{rate_identity}"
    allowed = await check_rate_limit(rate_key, max_requests=5, window_seconds=3600)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT",
                    "message": "Maximum 5 symptom checks per hour. Please try again later.",
                },
            },
        )

    # Get patient context if logged in
    patient_age = None
    known_conditions = []
    patient_id = None

    if user and user.role == "patient":
        result = await db.execute(
            select(PatientProfile).where(PatientProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if profile:
            patient_id = profile.id
            known_conditions = profile.chronic_conditions or []
            if profile.date_of_birth:
                from datetime import date
                today = date.today()
                patient_age = today.year - profile.date_of_birth.year

    # Call Gemini AI
    ai_response = await gemini_service.check_symptoms(
        symptoms=req.symptoms,
        language=req.language,
        patient_age=patient_age,
        known_conditions=known_conditions,
    )

    # Log to symptom_logs
    log = SymptomLog(
        patient_id=patient_id,
        symptoms_text=req.symptoms,
        language=req.language,
        ai_response=json.dumps(ai_response),
        urgency_level=ai_response.get("urgency", "medium"),
    )
    db.add(log)
    await db.commit()

    return _success(ai_response)
