"""Appointment model."""

import uuid
from datetime import datetime

from sqlalchemy import String, SmallInteger, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctor_profiles.id"), nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, default=15)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    type: Mapped[str] = mapped_column(String(20), default="video")
    daily_room_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    patient = relationship("PatientProfile", back_populates="appointments")
    doctor = relationship("DoctorProfile", back_populates="appointments")
    prescriptions = relationship("Prescription", back_populates="appointment")

    __table_args__ = (
        Index("idx_appt_patient", "patient_id", scheduled_at.desc()),
        Index("idx_appt_doctor", "doctor_id", "scheduled_at"),
    )
