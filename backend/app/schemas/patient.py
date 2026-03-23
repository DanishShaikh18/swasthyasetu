"""Patient schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class PatientProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    allergies: Optional[list[str]] = []
    chronic_conditions: Optional[list[str]] = []
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    preferred_language: Optional[str] = None

    model_config = {"from_attributes": True}


class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    allergies: Optional[list[str]] = None
    chronic_conditions: Optional[list[str]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    aadhaar_last4: Optional[str] = Field(None, max_length=4)
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None


class DocumentResponse(BaseModel):
    id: UUID
    document_type: Optional[str] = None
    file_name: Optional[str] = None
    file_url: str
    file_size_kb: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    document_type: Optional[str] = None
    file_name: Optional[str] = None
    file_url: str
    file_size_kb: Optional[int] = None
    notes: Optional[str] = None
    appointment_id: Optional[UUID] = None
