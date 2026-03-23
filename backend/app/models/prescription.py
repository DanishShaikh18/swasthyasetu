"""Prescription models — JSONB main table + flattened items for search."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    String, Boolean, SmallInteger, Text, Date,
    DateTime, ForeignKey, func, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctor_profiles.id"), nullable=False
    )
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    medicines = mapped_column(JSONB, nullable=False)
    advice: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    appointment = relationship("Appointment", back_populates="prescriptions")
    patient = relationship("PatientProfile", back_populates="prescriptions")
    doctor = relationship("DoctorProfile", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription")

    __table_args__ = (
        Index("idx_rx_medicines", medicines, postgresql_using="gin"),
    )


class PrescriptionItem(Base):
    """Flattened prescription items for search/queries."""
    __tablename__ = "prescription_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prescription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False
    )
    medicine_name: Mapped[str] = mapped_column(String(200), nullable=False)
    generic_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_days: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    prescription = relationship("Prescription", back_populates="items")

    __table_args__ = (
        Index("idx_rx_item_medicine", "medicine_name"),
    )
