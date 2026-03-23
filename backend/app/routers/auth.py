"""Auth router — register, login, refresh, logout."""

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.doctor import DoctorProfile
from app.models.pharmacy import PharmacyProfile
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    store_refresh_token, verify_refresh_token,
    revoke_refresh_token, blocklist_access_token,
)
from app.dependencies import get_current_user

router = APIRouter(tags=["Auth"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


def _error(code, message, status=400):
    raise HTTPException(status_code=status, detail={
        "success": False, "error": {"code": code, "message": message}
    })


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check existing
    existing = await db.execute(
        select(User).where((User.email == req.email) | (User.phone == req.phone))
    )
    if existing.scalar_one_or_none():
        _error("USER_EXISTS", "Email or phone already registered", 409)

    user = User(
        email=req.email,
        phone=req.phone,
        password_hash=hash_password(req.password),
        role=req.role,
        full_name=req.full_name,
        preferred_language=req.preferred_language,
        is_verified=req.role == "patient",  # patients auto-verified
    )
    db.add(user)
    await db.flush()

    # Create role-specific profile
    if req.role == "patient":
        profile = PatientProfile(user_id=user.id)
        db.add(profile)
    elif req.role == "doctor":
        if not req.specialization:
            _error("MISSING_FIELD", "Specialization required for doctors")
        profile = DoctorProfile(
            user_id=user.id,
            specialization=req.specialization,
            qualification=req.qualification,
            registration_number=req.registration_number,
            experience_years=req.experience_years,
            hospital_name=req.hospital_name,
            bio=req.bio,
            languages_spoken=req.languages_spoken or [],
            is_approved=False,
        )
        db.add(profile)
    elif req.role == "pharmacy":
        if not req.pharmacy_name or not req.address:
            _error("MISSING_FIELD", "Pharmacy name and address required")
        from geoalchemy2.elements import WKTElement
        lat = req.latitude or 28.6139
        lng = req.longitude or 77.2090
        location = WKTElement(f"POINT({lng} {lat})", srid=4326)
        profile = PharmacyProfile(
            user_id=user.id,
            pharmacy_name=req.pharmacy_name,
            license_number=req.license_number,
            address=req.address,
            village=req.village,
            district=req.district,
            state=req.state,
            location=location,
            phone=req.pharmacy_phone or req.phone,
            is_approved=False,
        )
        db.add(profile)

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(str(user.id), user.role, user.email)
    refresh_token = create_refresh_token(str(user.id))
    await store_refresh_token(str(user.id), refresh_token)

    return _success(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "role": user.role,
            "full_name": user.full_name,
            "is_approved": req.role == "patient",
        },
        "Registration successful"
    )


@router.post("/login")
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        _error("INVALID_CREDENTIALS", "Invalid email or password", 401)

    if not user.is_active:
        _error("ACCOUNT_DISABLED", "Account is disabled", 403)

    access_token = create_access_token(str(user.id), user.role, user.email)
    refresh_token = create_refresh_token(str(user.id))
    await store_refresh_token(str(user.id), refresh_token)

    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 86400,
    )

    # Check approval status for doctor/pharmacy
    is_approved = True
    if user.role == "doctor":
        doc = await db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == user.id)
        )
        doc_profile = doc.scalar_one_or_none()
        is_approved = doc_profile.is_approved if doc_profile else False
    elif user.role == "pharmacy":
        ph = await db.execute(
            select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
        )
        ph_profile = ph.scalar_one_or_none()
        is_approved = ph_profile.is_approved if ph_profile else False

    return _success({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "role": user.role,
        "full_name": user.full_name,
        "is_approved": is_approved,
        "preferred_language": user.preferred_language,
    })


@router.post("/refresh")
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    # Get refresh token from cookie or body
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    token = request.cookies.get("refresh_token") or body.get("refresh_token")

    if not token:
        _error("NO_TOKEN", "Refresh token required", 401)

    from jose import jwt, JWTError
    from app.config import settings
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            _error("INVALID_TOKEN", "Not a refresh token", 401)
        user_id = payload["user_id"]
    except JWTError:
        _error("INVALID_TOKEN", "Invalid or expired refresh token", 401)

    # Verify in Redis
    is_valid = await verify_refresh_token(user_id, token)
    if not is_valid:
        _error("REVOKED_TOKEN", "Refresh token revoked", 401)

    # Rotate: delete old, create new
    await revoke_refresh_token(user_id, token)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        _error("USER_NOT_FOUND", "User not found", 401)

    new_access = create_access_token(str(user.id), user.role, user.email)
    new_refresh = create_refresh_token(str(user.id))
    await store_refresh_token(str(user.id), new_refresh)

    response.set_cookie(
        key="refresh_token", value=new_refresh,
        httponly=True, secure=True, samesite="none", max_age=7 * 86400,
    )

    return _success({
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    })


@router.post("/logout")
async def logout(
    request: Request,
    user: User = Depends(get_current_user),
):
    # Blocklist access token
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        await blocklist_access_token(token)

    # Revoke refresh token
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await revoke_refresh_token(str(user.id), refresh_token)

    return _success(None, "Logged out successfully")
