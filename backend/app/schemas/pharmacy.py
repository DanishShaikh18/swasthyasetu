"""Pharmacy schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class PharmacyProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    pharmacy_name: str
    license_number: Optional[str] = None
    address: str
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    phone: str
    opening_hours: Optional[dict] = None
    is_approved: bool
    is_open_now: bool

    model_config = {"from_attributes": True}


class PharmacyProfileUpdate(BaseModel):
    pharmacy_name: Optional[str] = None
    license_number: Optional[str] = None
    address: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    opening_hours: Optional[dict] = None


class PharmacyStatusUpdate(BaseModel):
    is_open_now: bool


class InventoryItemResponse(BaseModel):
    id: UUID
    pharmacy_id: UUID
    medicine_name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    quantity_in_stock: int
    price_per_unit: Optional[float] = None
    unit: Optional[str] = None
    requires_prescription: bool
    last_updated: datetime

    model_config = {"from_attributes": True}


class InventoryItemCreate(BaseModel):
    medicine_name: str = Field(..., max_length=200)
    generic_name: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    quantity_in_stock: int = Field(default=0, ge=0)
    price_per_unit: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=30)
    requires_prescription: bool = False


class InventoryItemUpdate(BaseModel):
    medicine_name: Optional[str] = None
    generic_name: Optional[str] = None
    category: Optional[str] = None
    quantity_in_stock: Optional[int] = Field(None, ge=0)
    price_per_unit: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = None
    requires_prescription: Optional[bool] = None


class PharmacySearchResult(BaseModel):
    pharmacy_id: UUID
    pharmacy_name: str
    address: str
    phone: str
    distance_km: float
    is_open_now: bool
    medicine_name: str
    generic_name: Optional[str] = None
    quantity_in_stock: int
    price_per_unit: Optional[float] = None
    requires_prescription: bool
    last_updated: datetime
