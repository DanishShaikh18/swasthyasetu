"""Patient router — profile, prescriptions, appointments, documents."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User
from app.models.patient import PatientProfile, PatientDocument
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.doctor import DoctorProfile
from app.schemas.patient import (
    PatientProfileResponse, PatientProfileUpdate,
    DocumentCreate, DocumentResponse,
)
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.dependencies import get_current_user, require_role

router = APIRouter(tags=["Patient"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


@router.get("/me")
async def get_profile(
    user: User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return _success({
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": str(profile.date_of_birth) if profile.date_of_birth else None,
        "gender": profile.gender,
        "blood_group": profile.blood_group,
        "village": profile.village,
        "district": profile.district,
        "state": profile.state,
        "allergies": profile.allergies or [],
        "chronic_conditions": profile.chronic_conditions or [],
        "emergency_contact_name": profile.emergency_contact_name,
        "emergency_contact_phone": profile.emergency_contact_phone,
        "preferred_language": user.preferred_language,
    })


@router.patch("/me")
async def update_profile(
    data: PatientProfileUpdate,
    user: User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = data.model_dump(exclude_unset=True)
    # Handle user-level fields
    if "full_name" in update_data:
        user.full_name = update_data.pop("full_name")
    if "preferred_language" in update_data:
        user.preferred_language = update_data.pop("preferred_language")

    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    return _success(None, "Profile updated")


@router.get("/me/prescriptions")
async def get_prescriptions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    active_only: bool = Query(False),
    user: User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    query = select(Prescription).where(Prescription.patient_id == profile.id)
    if active_only:
        query = query.where(Prescription.is_active == True)
    query = query.order_by(desc(Prescription.created_at))
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    prescriptions = result.scalars().all()

    items = []
    for rx in prescriptions:
        # Get doctor name
        doc_result = await db.execute(
            select(DoctorProfile).options(joinedload(DoctorProfile.user))
            .where(DoctorProfile.id == rx.doctor_id)
        )
        doc = doc_result.scalar_one_or_none()
        items.append({
            "id": str(rx.id),
            "doctor_name": doc.user.full_name if doc else "Unknown",
            "doctor_specialization": doc.specialization if doc else "",
            "diagnosis": rx.diagnosis,
            "medicines": rx.medicines,
            "advice": rx.advice,
            "follow_up_date": str(rx.follow_up_date) if rx.follow_up_date else None,
            "is_active": rx.is_active,
            "created_at": rx.created_at.isoformat(),
        })

    return _success({"items": items, "page": page, "limit": limit})


@router.get("/me/appointments")
async def get_appointments(
    status: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    query = select(Appointment).where(Appointment.patient_id == profile.id)
    if status:
        query = query.where(Appointment.status == status)
    query = query.order_by(desc(Appointment.scheduled_at))
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    appointments = result.scalars().all()

    items = []
    for appt in appointments:
        doc_result = await db.execute(
            select(DoctorProfile).options(joinedload(DoctorProfile.user))
            .where(DoctorProfile.id == appt.doctor_id)
        )
        doc = doc_result.scalar_one_or_none()
        items.append({
            "id": str(appt.id),
            "doctor_name": doc.user.full_name if doc else "Unknown",
            "doctor_specialization": doc.specialization if doc else "",
            "scheduled_at": appt.scheduled_at.isoformat(),
            "duration_minutes": appt.duration_minutes,
            "status": appt.status,
            "type": appt.type,
            "chief_complaint": appt.chief_complaint,
            "created_at": appt.created_at.isoformat(),
        })

    return _success({"items": items, "page": page, "limit": limit})


@router.post("/appointments")
async def book_appointment(
    data: AppointmentCreate,
    user: User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    # Get patient profile
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Check doctor exists and is approved (caller may pass user_id or profile_id)
    doc_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.id == data.doctor_id)
    )
    doctor = doc_result.scalar_one_or_none()
    if not doctor:
        doc_result = await db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == data.doctor_id)
        )
        doctor = doc_result.scalar_one_or_none()
    if not doctor or not doctor.is_approved:
        raise HTTPException(status_code=404, detail="Doctor not found or not approved")

    # Try to book the slot
    from sqlalchemy import text, update
    from app.models.doctor import DoctorAvailableSlot

    result = await db.execute(
        select(DoctorAvailableSlot).where(
            DoctorAvailableSlot.doctor_id == doctor.id,
            DoctorAvailableSlot.slot_time == data.slot_time,
            DoctorAvailableSlot.status == "available",
        )
    )
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=409, detail="Slot not available")

    # Create appointment
    appointment = Appointment(
        patient_id=profile.id,
        doctor_id=doctor.id,
        scheduled_at=data.slot_time,
        type=data.type,
        chief_complaint=data.chief_complaint,
        status="confirmed",
    )
    db.add(appointment)
    await db.flush()

    # Mark slot as booked
    slot.status = "booked"
    slot.appointment_id = appointment.id
    await db.commit()

    # Send notification to doctor
    from app.services import notification_service
    doc_user_result = await db.execute(select(User).where(User.id == doctor.user_id))
    doc_user = doc_user_result.scalar_one_or_none()
    if doc_user:
        await notification_service.send(
            db, doc_user.id, "appt_confirmed",
            "New Appointment", f"{user.full_name} booked an appointment",
            fcm_token=doc_user.fcm_token,
        )

    return _success({
        "appointment_id": str(appointment.id),
        "scheduled_at": appointment.scheduled_at.isoformat(),
        "status": appointment.status,
    }, "Appointment booked successfully")


@router.get("/me/documents")
async def get_documents(
    user: User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    docs = await db.execute(
        select(PatientDocument)
        .where(PatientDocument.patient_id == profile.id)
        .order_by(desc(PatientDocument.created_at))
    )
    documents = docs.scalars().all()
    items = [{
        "id": str(d.id),
        "document_type": d.document_type,
        "file_name": d.file_name,
        "file_url": d.file_url,
        "file_size_kb": d.file_size_kb,
        "notes": d.notes,
        "created_at": d.created_at.isoformat(),
    } for d in documents]

    return _success(items)


@router.post("/me/documents")
async def upload_document(
    data: DocumentCreate,
    user: User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    doc = PatientDocument(
        patient_id=profile.id,
        uploaded_by=user.id,
        document_type=data.document_type,
        file_name=data.file_name,
        file_url=data.file_url,
        file_size_kb=data.file_size_kb,
        notes=data.notes,
        appointment_id=data.appointment_id,
    )
    db.add(doc)
    await db.commit()
    return _success({"document_id": str(doc.id)}, "Document saved")
