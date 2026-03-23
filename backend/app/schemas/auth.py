"""Auth schemas — registration, login, tokens."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=150)
    role: str = Field(..., pattern="^(patient|doctor|pharmacy)$")
    preferred_language: str = Field(default="hi", max_length=10)

    # Optional doctor fields
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    registration_number: Optional[str] = None
    experience_years: Optional[int] = None
    hospital_name: Optional[str] = None
    bio: Optional[str] = None
    languages_spoken: Optional[list[str]] = None

    # Optional pharmacy fields
    pharmacy_name: Optional[str] = None
    license_number: Optional[str] = None
    address: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pharmacy_phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    role: str
    full_name: str


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None  # can also come from cookie
