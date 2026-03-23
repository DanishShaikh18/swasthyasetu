"""Pharmacy-related models — profile with PostGIS location, medicine inventory."""

import uuid
from datetime import datetime

from sqlalchemy import (
    String, Boolean, Integer, Numeric, Text,
    DateTime, ForeignKey, func, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geography
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PharmacyProfile(Base):
    __tablename__ = "pharmacy_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    pharmacy_name: Mapped[str] = mapped_column(String(200), nullable=False)
    license_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    village: Mapped[str | None] = mapped_column(String(150), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    opening_hours = mapped_column(JSONB, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_open_now: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="pharmacy_profile")
    inventory = relationship("MedicineInventory", back_populates="pharmacy")

    __table_args__ = (
        Index("idx_pharmacy_location", location, postgresql_using="gist"),
    )


class MedicineInventory(Base):
    __tablename__ = "medicine_inventory"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacy_profiles.id"), nullable=False
    )
    medicine_name: Mapped[str] = mapped_column(String(200), nullable=False)
    generic_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, default=0)
    price_per_unit: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)
    requires_prescription: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    pharmacy = relationship("PharmacyProfile", back_populates="inventory")

    __table_args__ = (
        Index("idx_medicine_pharmacy", "pharmacy_id", "quantity_in_stock"),
    )
