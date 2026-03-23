"""Doctor router — profile, appointments, patients, prescriptions, slots."""

from uuid import UUID
from datetime import datetime, timedelta, timezone, time as dt_time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User
from app.models.doctor import DoctorProfile, DoctorSlot, DoctorAvailableSlot
from app.models.patient import PatientProfile
from app.models.appointment import Appointment
from app.models.prescription import Prescription, PrescriptionItem
from app.models.notification import AuditLog
from app.schemas.doctor import (
    DoctorProfileResponse, DoctorProfileUpdate, DoctorAvailabilityUpdate,
    SlotTemplateCreate, SlotTemplateResponse, AvailableSlotResponse,
    AppointmentStatusUpdate,
)
from app.schemas.ai import PrescriptionCreate
from app.dependencies import get_current_user, require_role
from app.services import notification_service

router = APIRouter(tags=["Doctor"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


@router.get("")
async def list_doctors(
    specialization: str = Query(None),
    language: str = Query(None),
    state: str = Query(None),
    available_now: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — list approved doctors with filters."""
    query = (
        select(DoctorProfile)
        .options(joinedload(DoctorProfile.user))
        .where(DoctorProfile.is_approved == True)
    )
    if specialization:
        query = query.where(DoctorProfile.specialization.ilike(f"%{specialization}%"))
    if available_now:
        query = query.where(DoctorProfile.is_available == True)
    if language:
        query = query.where(DoctorProfile.languages_spoken.any(language))

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    doctors = result.unique().scalars().all()

    items = []
    for doc in doctors:
        items.append({
            "id": str(doc.id),
            "full_name": doc.user.full_name if doc.user else "",
            "specialization": doc.specialization,
            "qualification": doc.qualification,
            "experience_years": doc.experience_years,
            "languages_spoken": doc.languages_spoken or [],
            "consultation_fee": float(doc.consultation_fee or 0),
            "is_available": doc.is_available,
            "hospital_name": doc.hospital_name,
            "bio": doc.bio,
            "avatar_url": doc.avatar_url,
        })

    return _success({"items": items, "page": page, "limit": limit})


@router.get("/{doctor_id}/slots")
async def get_available_slots(
    doctor_id: UUID,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Public — get available slots for a doctor."""
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)

    result = await db.execute(
        select(DoctorAvailableSlot)
        .where(
            DoctorAvailableSlot.doctor_id == doctor_id,
            DoctorAvailableSlot.slot_time >= now,
            DoctorAvailableSlot.slot_time <= end,
            DoctorAvailableSlot.status == "available",
        )
        .order_by(DoctorAvailableSlot.slot_time)
    )
    slots = result.scalars().all()
    return _success([{
        "id": str(s.id),
        "slot_time": s.slot_time.isoformat(),
        "status": s.status,
    } for s in slots])


@router.get("/me/profile")
async def get_doctor_profile(
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return _success({
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "full_name": user.full_name,
        "email": user.email,
        "specialization": profile.specialization,
        "qualification": profile.qualification,
        "registration_number": profile.registration_number,
        "experience_years": profile.experience_years,
        "languages_spoken": profile.languages_spoken or [],
        "consultation_fee": float(profile.consultation_fee or 0),
        "is_available": profile.is_available,
        "hospital_name": profile.hospital_name,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "is_approved": profile.is_approved,
    })


@router.patch("/me/profile")
async def update_doctor_profile(
    data: DoctorProfileUpdate,
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = data.model_dump(exclude_unset=True)
    if "full_name" in update_data:
        user.full_name = update_data.pop("full_name")
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    return _success(None, "Profile updated")


@router.patch("/me/availability")
async def toggle_availability(
    data: DoctorAvailabilityUpdate,
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.is_available = data.is_available
    await db.commit()
    return _success({"is_available": profile.is_available})


@router.get("/me/appointments")
async def get_doctor_appointments(
    date: str = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    doc_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Profile not found")

    query = select(Appointment).where(Appointment.doctor_id == doc.id)
    if status:
        query = query.where(Appointment.status == status)
    if date:
        target = datetime.fromisoformat(date)
        query = query.where(
            Appointment.scheduled_at >= target,
            Appointment.scheduled_at < target + timedelta(days=1),
        )
    query = query.order_by(Appointment.scheduled_at).offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    appointments = result.scalars().all()

    items = []
    for appt in appointments:
        pat_result = await db.execute(
            select(PatientProfile).options(joinedload(PatientProfile.user))
            .where(PatientProfile.id == appt.patient_id)
        )
        patient = pat_result.scalar_one_or_none()
        age = None
        if patient and patient.date_of_birth:
            age = (datetime.now().date() - patient.date_of_birth).days // 365

        items.append({
            "id": str(appt.id),
            "patient_id": str(appt.patient_id),
            "patient_name": patient.user.full_name if patient and patient.user else "Unknown",
            "patient_age": age,
            "patient_gender": patient.gender if patient else None,
            "scheduled_at": appt.scheduled_at.isoformat(),
            "duration_minutes": appt.duration_minutes,
            "status": appt.status,
            "type": appt.type,
            "chief_complaint": appt.chief_complaint,
            "notes": appt.notes,
            "created_at": appt.created_at.isoformat(),
        })

    return _success({"items": items, "page": page, "limit": limit})


@router.patch("/me/appointments/{appointment_id}")
async def update_appointment(
    appointment_id: UUID,
    data: AppointmentStatusUpdate,
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    doc_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    doc = doc_result.scalar_one_or_none()

    appt_result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.doctor_id == doc.id,
        )
    )
    appt = appt_result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if data.status:
        appt.status = data.status
    if data.notes:
        appt.notes = data.notes

    await db.commit()
    return _success(None, "Appointment updated")


@router.get("/me/patients/{patient_id}")
async def get_patient_record(
    patient_id: UUID,
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    """View patient record — only if doctor has appointment with this patient."""
    doc_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    doc = doc_result.scalar_one_or_none()

    # Check appointment relationship
    appt_check = await db.execute(
        select(Appointment).where(
            Appointment.doctor_id == doc.id,
            Appointment.patient_id == patient_id,
        ).limit(1)
    )
    if not appt_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="No appointment with this patient")

    patient_result = await db.execute(
        select(PatientProfile).options(joinedload(PatientProfile.user))
        .where(PatientProfile.id == patient_id)
    )
    patient = patient_result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Audit log
    audit = AuditLog(
        actor_id=user.id, actor_role="doctor",
        action="VIEW_PATIENT_RECORD", resource_type="patient",
        resource_id=patient_id,
    )
    db.add(audit)
    await db.flush()

    # Get prescriptions
    rx_result = await db.execute(
        select(Prescription).where(Prescription.patient_id == patient_id)
        .order_by(desc(Prescription.created_at)).limit(20)
    )
    prescriptions = rx_result.scalars().all()

    return _success({
        "patient": {
            "id": str(patient.id),
            "full_name": patient.user.full_name,
            "date_of_birth": str(patient.date_of_birth) if patient.date_of_birth else None,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "village": patient.village,
            "district": patient.district,
            "state": patient.state,
            "allergies": patient.allergies or [],
            "chronic_conditions": patient.chronic_conditions or [],
        },
        "prescriptions": [{
            "id": str(rx.id),
            "diagnosis": rx.diagnosis,
            "medicines": rx.medicines,
            "advice": rx.advice,
            "created_at": rx.created_at.isoformat(),
        } for rx in prescriptions],
    })


@router.post("/me/prescriptions")
async def write_prescription(
    data: PrescriptionCreate,
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    """Dual write — prescriptions table (JSONB) + prescription_items (flat)."""
    doc_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    from datetime import date
    follow_up = None
    if data.follow_up_date:
        try:
            follow_up = date.fromisoformat(data.follow_up_date)
        except ValueError:
            pass

    # Dual write in single transaction
    async with db.begin_nested():
        rx = Prescription(
            appointment_id=data.appointment_id,
            patient_id=data.patient_id,
            doctor_id=doc.id,
            diagnosis=data.diagnosis,
            medicines=data.medicines,
            advice=data.advice,
            follow_up_date=follow_up,
        )
        db.add(rx)
        await db.flush()

        for med in data.medicines:
            item = PrescriptionItem(
                prescription_id=rx.id,
                medicine_name=med.get("name", ""),
                generic_name=med.get("generic_name"),
                dosage=med.get("dosage"),
                frequency=med.get("frequency"),
                duration_days=med.get("duration_days"),
                instructions=med.get("instructions"),
            )
            db.add(item)

        # Audit log
        audit = AuditLog(
            actor_id=user.id, actor_role="doctor",
            action="WRITE_PRESCRIPTION", resource_type="prescription",
            resource_id=rx.id,
        )
        db.add(audit)

    await db.commit()

    # Notify patient
    pat_result = await db.execute(
        select(PatientProfile).options(joinedload(PatientProfile.user))
        .where(PatientProfile.id == data.patient_id)
    )
    patient = pat_result.scalar_one_or_none()
    if patient and patient.user:
        await notification_service.send(
            db, patient.user.id, "prescription_ready",
            "New Prescription",
            f"Dr. {user.full_name} has written a prescription for you",
            fcm_token=patient.user.fcm_token,
        )
        await db.commit()

    return _success({"prescription_id": str(rx.id)}, "Prescription created")


@router.get("/me/slots")
async def get_slot_templates(
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    doc_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    doc = doc_result.scalar_one_or_none()

    result = await db.execute(
        select(DoctorSlot).where(DoctorSlot.doctor_id == doc.id, DoctorSlot.is_active == True)
        .order_by(DoctorSlot.day_of_week, DoctorSlot.start_time)
    )
    slots = result.scalars().all()
    return _success([{
        "id": str(s.id),
        "day_of_week": s.day_of_week,
        "start_time": s.start_time.strftime("%H:%M"),
        "end_time": s.end_time.strftime("%H:%M"),
        "slot_duration_min": s.slot_duration_min,
        "is_active": s.is_active,
    } for s in slots])


@router.post("/me/slots")
async def create_slot_template(
    data: SlotTemplateCreate,
    user: User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    doc_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )
    doc = doc_result.scalar_one_or_none()

    start = dt_time.fromisoformat(data.start_time)
    end = dt_time.fromisoformat(data.end_time)

    slot = DoctorSlot(
        doctor_id=doc.id,
        day_of_week=data.day_of_week,
        start_time=start,
        end_time=end,
        slot_duration_min=data.slot_duration_min,
    )
    db.add(slot)
    await db.commit()

    # Generate available slots for the next 30 days
    await _generate_slots_for_template(doc.id, slot, db)

    return _success({"slot_id": str(slot.id)}, "Slot template created")


async def _generate_slots_for_template(
    doctor_id: UUID, template: DoctorSlot, db: AsyncSession
):
    """Generate individual bookable slots from a weekly template."""
    now = datetime.now(timezone.utc)
    for day_offset in range(30):
        target_date = now.date() + timedelta(days=day_offset)
        if target_date.weekday() == template.day_of_week:
            current = datetime.combine(target_date, template.start_time, tzinfo=timezone.utc)
            end = datetime.combine(target_date, template.end_time, tzinfo=timezone.utc)
            while current < end:
                if current > now:
                    existing = await db.execute(
                        select(DoctorAvailableSlot).where(
                            DoctorAvailableSlot.doctor_id == doctor_id,
                            DoctorAvailableSlot.slot_time == current,
                        )
                    )
                    if not existing.scalar_one_or_none():
                        db.add(DoctorAvailableSlot(
                            doctor_id=doctor_id,
                            slot_time=current,
                            status="available",
                        ))
                current += timedelta(minutes=template.slot_duration_min)
    await db.commit()
