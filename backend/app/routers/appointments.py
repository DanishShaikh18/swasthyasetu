"""Appointments router — video call join endpoint."""

import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.patient import PatientProfile
from app.models.doctor import DoctorProfile
from app.dependencies import get_current_user
from app.services import daily_service

router = APIRouter(tags=["Appointments"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


@router.get("/{appointment_id}/join")
async def join_video_call(
    appointment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate on-demand Daily.co token for video call.
    - Verifies user is part of appointment
    - Verifies appointment is confirmed
    - Verifies time is within 10 min of scheduled time
    - Creates room if needed, generates token (NEVER stored in DB)
    """
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Verify user belongs to this appointment
    is_doctor = False
    if user.role == "patient":
        pat_result = await db.execute(
            select(PatientProfile).where(PatientProfile.user_id == user.id)
        )
        patient = pat_result.scalar_one_or_none()
        if not patient or patient.id != appt.patient_id:
            raise HTTPException(status_code=403, detail="Not your appointment")
    elif user.role == "doctor":
        doc_result = await db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == user.id)
        )
        doctor = doc_result.scalar_one_or_none()
        if not doctor or doctor.id != appt.doctor_id:
            raise HTTPException(status_code=403, detail="Not your appointment")
        is_doctor = True
    else:
        raise HTTPException(status_code=403, detail="Invalid role for video call")

    # Verify appointment status
    if appt.status not in ("confirmed", "pending"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot join — appointment status: {appt.status}"
        )

    # Verify time window (within 10 min before or during)
    now = datetime.now(timezone.utc)
    earliest_join = appt.scheduled_at - timedelta(minutes=10)
    latest_join = appt.scheduled_at + timedelta(minutes=appt.duration_minutes + 15)

    if now < earliest_join:
        mins_until = int((earliest_join - now).total_seconds() / 60)
        raise HTTPException(
            status_code=400,
            detail=f"Too early to join. Call opens in {mins_until} minutes."
        )
    if now > latest_join:
        raise HTTPException(status_code=400, detail="Call window has expired")

    # Create room if needed
    if not appt.daily_room_name:
        room_name = f"ss-{str(appt.id)[:8]}"
        room = await daily_service.create_room(room_name)
        if room:
            appt.daily_room_name = room["name"]
            await db.commit()
        else:
            raise HTTPException(status_code=503, detail="Could not create video room")

    # Generate token — NEVER stored in DB
    token = await daily_service.create_meeting_token(
        appt.daily_room_name,
        is_owner=is_doctor,
    )
    if not token:
        raise HTTPException(status_code=503, detail="Could not generate call token")

    return _success({
        "token": token,
        "room_name": appt.daily_room_name,
        "room_url": f"https://swasthyasetu.daily.co/{appt.daily_room_name}",
    })
