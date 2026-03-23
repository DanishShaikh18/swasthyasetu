"""AI and content schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class SymptomCheckRequest(BaseModel):
    symptoms: str = Field(..., min_length=3, max_length=2000)
    language: str = Field(default="hi", max_length=5)


class SymptomCheckResponse(BaseModel):
    possible_condition: str
    urgency: str
    urgency_color: str
    advice: str
    see_doctor_now: bool
    call_emergency: bool
    disclaimer: str


class PrescriptionCreate(BaseModel):
    appointment_id: Optional[UUID] = None
    patient_id: UUID
    diagnosis: Optional[str] = None
    medicines: list[dict] = Field(..., min_length=1)
    advice: Optional[str] = None
    follow_up_date: Optional[str] = None  # "YYYY-MM-DD"


class PrescriptionResponse(BaseModel):
    id: UUID
    appointment_id: Optional[UUID] = None
    patient_id: UUID
    doctor_id: UUID
    doctor_name: Optional[str] = None
    diagnosis: Optional[str] = None
    medicines: list[dict]
    advice: Optional[str] = None
    follow_up_date: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentResponse(BaseModel):
    id: UUID
    type: str
    title: str
    body: str
    language: str
    state: Optional[str] = None
    season: Optional[str] = None

    model_config = {"from_attributes": True}


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    body: str
    data: Optional[dict] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
