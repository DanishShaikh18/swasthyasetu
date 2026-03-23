"""Appointment schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class AppointmentCreate(BaseModel):
    doctor_id: UUID
    slot_time: datetime
    type: str = Field(default="video", pattern="^(video|audio)$")
    chief_complaint: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int
    status: str
    type: str
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoCallToken(BaseModel):
    token: str
    room_name: str
    room_url: str
