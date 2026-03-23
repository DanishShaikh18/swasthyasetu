"""Doctor schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import time, datetime, date


class DoctorProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    specialization: str
    qualification: Optional[str] = None
    registration_number: Optional[str] = None
    experience_years: Optional[int] = None
    languages_spoken: Optional[list[str]] = []
    consultation_fee: Optional[float] = 0
    is_available: bool = False
    hospital_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_approved: bool = False

    model_config = {"from_attributes": True}


class DoctorProfileUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    registration_number: Optional[str] = None
    experience_years: Optional[int] = None
    languages_spoken: Optional[list[str]] = None
    consultation_fee: Optional[float] = None
    hospital_name: Optional[str] = None
    bio: Optional[str] = None
    full_name: Optional[str] = None


class DoctorAvailabilityUpdate(BaseModel):
    is_available: bool


class SlotTemplateCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str  # "09:00"
    end_time: str    # "17:00"
    slot_duration_min: int = Field(default=15, ge=5, le=60)


class SlotTemplateResponse(BaseModel):
    id: UUID
    day_of_week: int
    start_time: str
    end_time: str
    slot_duration_min: int
    is_active: bool

    model_config = {"from_attributes": True}


class AvailableSlotResponse(BaseModel):
    id: UUID
    slot_time: datetime
    status: str

    model_config = {"from_attributes": True}


class DoctorAppointmentResponse(BaseModel):
    id: UUID
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int
    status: str
    type: str
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AppointmentStatusUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(confirmed|completed|cancelled|no_show)$")
    reschedule_to: Optional[datetime] = None
    notes: Optional[str] = None
