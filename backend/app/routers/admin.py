"""Admin router manage doctor and pharmacy approvals."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.doctor import DoctorProfile
from app.models.pharmacy import PharmacyProfile
from app.dependencies import get_current_user

router = APIRouter(tags=["Admin"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


def _error(code, message, status=400):
    raise HTTPException(status_code=status, detail={
        "success": False, "error": {"code": code, "message": message}
    })


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Only admin role can access these endpoints."""
    if user.role != "admin":
        _error("FORBIDDEN", "Admin access required", 403)
    return user


# ── DOCTORS ──────────────────────────────────────────────────────────────────

@router.get("/doctors/pending")
async def get_pending_doctors(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all doctors waiting for approval."""
    result = await db.execute(
        select(DoctorProfile)
        .options(selectinload(DoctorProfile.user))
        .where(DoctorProfile.is_approved == False)
    )
    profiles = result.scalars().all()

    data = [
        {
            "doctor_profile_id": str(p.id),
            "user_id": str(p.user_id),
            "full_name": p.user.full_name,
            "email": p.user.email,
            "phone": p.user.phone,
            "specialization": p.specialization,
            "qualification": p.qualification,
            "registration_number": p.registration_number,
            "experience_years": p.experience_years,
            "hospital_name": p.hospital_name,
        }
        for p in profiles
    ]
    return _success(data, f"{len(data)} pending doctors")


@router.post("/doctors/{doctor_profile_id}/approve")
async def approve_doctor(
    doctor_profile_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Approve a doctor by their doctor_profile id."""
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.id == doctor_profile_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        _error("NOT_FOUND", "Doctor profile not found", 404)

    if profile.is_approved:
        _error("ALREADY_APPROVED", "Doctor is already approved", 400)

    profile.is_approved = True
    await db.commit()

    return _success(
        {"doctor_profile_id": str(profile.id), "is_approved": True},
        "Doctor approved successfully"
    )


@router.post("/doctors/{doctor_profile_id}/reject")
async def reject_doctor(
    doctor_profile_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Reject/revoke a doctor approval."""
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.id == doctor_profile_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        _error("NOT_FOUND", "Doctor profile not found", 404)

    profile.is_approved = False
    await db.commit()

    return _success(
        {"doctor_profile_id": str(profile.id), "is_approved": False},
        "Doctor approval revoked"
    )


# ── PHARMACY ─────────────────────────────────────────────────────────────────

@router.get("/pharmacy/pending")
async def get_pending_pharmacies(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all pharmacies waiting for approval."""
    result = await db.execute(
        select(PharmacyProfile)
        .options(selectinload(PharmacyProfile.user))
        .where(PharmacyProfile.is_approved == False)
    )
    profiles = result.scalars().all()

    data = [
        {
            "pharmacy_profile_id": str(p.id),
            "user_id": str(p.user_id),
            "full_name": p.user.full_name,
            "email": p.user.email,
            "pharmacy_name": p.pharmacy_name,
            "license_number": p.license_number,
            "address": p.address,
            "district": p.district,
            "state": p.state,
            "phone": p.phone,
        }
        for p in profiles
    ]
    return _success(data, f"{len(data)} pending pharmacies")


@router.post("/pharmacy/{pharmacy_profile_id}/approve")
async def approve_pharmacy(
    pharmacy_profile_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Approve a pharmacy by their pharmacy_profile id."""
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.id == pharmacy_profile_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        _error("NOT_FOUND", "Pharmacy profile not found", 404)

    if profile.is_approved:
        _error("ALREADY_APPROVED", "Pharmacy is already approved", 400)

    profile.is_approved = True
    await db.commit()

    return _success(
        {"pharmacy_profile_id": str(profile.id), "is_approved": True},
        "Pharmacy approved successfully"
    )


@router.post("/pharmacy/{pharmacy_profile_id}/reject")
async def reject_pharmacy(
    pharmacy_profile_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Reject/revoke a pharmacy approval."""
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.id == pharmacy_profile_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        _error("NOT_FOUND", "Pharmacy profile not found", 404)

    profile.is_approved = False
    await db.commit()

    return _success(
        {"pharmacy_profile_id": str(profile.id), "is_approved": False},
        "Pharmacy approval revoked"
    )