"""Patient-related models — profile, documents, symptom logs."""

import uuid
from datetime import date, datetime

from sqlalchemy import String, Boolean, Date, DateTime, Text, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    village: Mapped[str | None] = mapped_column(String(150), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    allergies = mapped_column(ARRAY(Text), default=list)
    chronic_conditions = mapped_column(ARRAY(Text), default=list)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    aadhaar_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    documents = relationship("PatientDocument", back_populates="patient")


class PatientDocument(Base):
    __tablename__ = "patient_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    document_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    patient = relationship("PatientProfile", back_populates="documents")


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=True
    )
    symptoms_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(5), nullable=True)
    ai_response = mapped_column(Text, nullable=True)  # stored as JSON string
    urgency_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
