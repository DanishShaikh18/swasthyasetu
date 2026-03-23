"""Doctor-related models — profile, weekly slot templates, available slots."""

import uuid
from datetime import time, datetime

from sqlalchemy import (
    String, Boolean, SmallInteger, Numeric, Text, Time,
    DateTime, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[str | None] = mapped_column(String(100), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    languages_spoken = mapped_column(ARRAY(Text), default=list)
    consultation_fee: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False)
    hospital_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    slots = relationship("DoctorSlot", back_populates="doctor")
    available_slots = relationship("DoctorAvailableSlot", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")


class DoctorSlot(Base):
    """Weekly schedule template — defines recurring availability."""
    __tablename__ = "doctor_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctor_profiles.id"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration_min: Mapped[int] = mapped_column(SmallInteger, default=15)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    doctor = relationship("DoctorProfile", back_populates="slots")


class DoctorAvailableSlot(Base):
    """Pre-generated actual bookable slots."""
    __tablename__ = "doctor_available_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctor_profiles.id"), nullable=False
    )
    slot_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="available")
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True
    )

    doctor = relationship("DoctorProfile", back_populates="available_slots")
