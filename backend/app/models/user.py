"""User model — central authentication table for all roles."""

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="hi")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    fcm_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    pharmacy_profile = relationship("PharmacyProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
