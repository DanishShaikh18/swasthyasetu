"""Pharmacy router — search (PostGIS), profile, inventory CRUD, CSV bulk upload."""

import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, desc

from app.database import get_db
from app.models.user import User
from app.models.pharmacy import PharmacyProfile, MedicineInventory
from app.schemas.pharmacy import (
    PharmacyProfileUpdate, PharmacyStatusUpdate,
    InventoryItemCreate, InventoryItemUpdate,
)
from app.dependencies import get_current_user, require_role

router = APIRouter(tags=["Pharmacy"])


def _success(data, message="Success"):
    return {"success": True, "data": data, "message": message}


@router.get("/search")
async def search_pharmacies(
    medicine: str = Query(..., min_length=2),
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(20, ge=1, le=100),
    in_stock: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """Public PostGIS geospatial pharmacy search with trigram matching."""
    radius_meters = radius_km * 1000

    query = text("""
        SELECT
            p.id as pharmacy_id,
            p.pharmacy_name,
            p.address,
            p.phone,
            p.is_open_now,
            mi.id as medicine_id,
            mi.medicine_name,
            mi.generic_name,
            mi.quantity_in_stock,
            mi.price_per_unit,
            mi.requires_prescription,
            mi.last_updated,
            ST_Distance(
                p.location,
                ST_MakePoint(:lng, :lat)::geography
            ) AS dist_meters
        FROM pharmacy_profiles p
        JOIN medicine_inventory mi ON mi.pharmacy_id = p.id
        WHERE p.is_approved = true
          AND ST_DWithin(
                p.location,
                ST_MakePoint(:lng, :lat)::geography,
                :radius_meters
          )
          AND (
              mi.medicine_name ILIKE '%' || :medicine || '%'
              OR mi.generic_name ILIKE '%' || :medicine || '%'
          )
          AND (:in_stock = false OR mi.quantity_in_stock > 0)
        ORDER BY dist_meters
        LIMIT 20
    """)

    result = await db.execute(query, {
        "lat": lat, "lng": lng,
        "medicine": medicine,
        "radius_meters": radius_meters,
        "in_stock": in_stock,
    })
    rows = result.fetchall()

    items = []
    for row in rows:
        items.append({
            "pharmacy_id": str(row.pharmacy_id),
            "pharmacy_name": row.pharmacy_name,
            "address": row.address,
            "phone": row.phone,
            "is_open_now": row.is_open_now,
            "distance_km": round(row.dist_meters / 1000, 1),
            "medicine_name": row.medicine_name,
            "generic_name": row.generic_name,
            "quantity_in_stock": row.quantity_in_stock,
            "price_per_unit": float(row.price_per_unit) if row.price_per_unit else None,
            "requires_prescription": row.requires_prescription,
            "last_updated": row.last_updated.isoformat() if row.last_updated else None,
        })

    return _success(items)


@router.get("/me/profile")
async def get_pharmacy_profile(
    user: User = Depends(require_role("pharmacy")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return _success({
        "id": str(profile.id),
        "pharmacy_name": profile.pharmacy_name,
        "license_number": profile.license_number,
        "address": profile.address,
        "village": profile.village,
        "district": profile.district,
        "state": profile.state,
        "phone": profile.phone,
        "opening_hours": profile.opening_hours,
        "is_approved": profile.is_approved,
        "is_open_now": profile.is_open_now,
    })


@router.patch("/me/profile")
async def update_pharmacy_profile(
    data: PharmacyProfileUpdate,
    user: User = Depends(require_role("pharmacy")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    return _success(None, "Profile updated")


@router.patch("/me/status")
async def toggle_status(
    data: PharmacyStatusUpdate,
    user: User = Depends(require_role("pharmacy")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.is_open_now = data.is_open_now
    await db.commit()
    return _success({"is_open_now": profile.is_open_now})


@router.get("/me/inventory")
async def get_inventory(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(require_role("pharmacy")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    query = select(MedicineInventory).where(MedicineInventory.pharmacy_id == profile.id)
    if search:
        query = query.where(
            MedicineInventory.medicine_name.ilike(f"%{search}%") |
            MedicineInventory.generic_name.ilike(f"%{search}%")
        )
    query = query.order_by(MedicineInventory.medicine_name)
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    return _success({
        "items": [{
            "id": str(item.id),
            "medicine_name": item.medicine_name,
            "generic_name": item.generic_name,
            "category": item.category,
            "quantity_in_stock": item.quantity_in_stock,
            "price_per_unit": float(item.price_per_unit) if item.price_per_unit else None,
            "unit": item.unit,
            "requires_prescription": item.requires_prescription,
            "last_updated": item.last_updated.isoformat() if item.last_updated else None,
        } for item in items],
        "page": page,
        "limit": limit,
    })


@router.post("/me/inventory")
async def add_inventory_item(
    data: InventoryItemCreate,
    user: User = Depends(require_role("pharmacy")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    item = MedicineInventory(
        pharmacy_id=profile.id,
        **data.model_dump()
    )
    db.add(item)
    await db.commit()
    return _success({"item_id": str(item.id)}, "Medicine added")


@router.patch("/me/inventory/{item_id}")
async def update_inventory_item(
    item_id: UUID,
    data: InventoryItemUpdate,
    user: User = Depends(require_role("pharmacy")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    item_result = await db.execute(
        select(MedicineInventory).where(
            MedicineInventory.id == item_id,
            MedicineInventory.pharmacy_id == profile.id,
        )
    )
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    return _success(None, "Item updated")


@router.post("/me/inventory/bulk")
async def bulk_upload_inventory(
    file: UploadFile = File(...),
    user: User = Depends(require_role("pharmacy")),
    db: AsyncSession = Depends(get_db),
):
    """CSV bulk upload for medicine inventory."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    result = await db.execute(
        select(PharmacyProfile).where(PharmacyProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    content = await file.read()
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))

    inserted = 0
    updated = 0
    errors = []
    row_num = 1

    for row in reader:
        row_num += 1
        try:
            medicine_name = row.get("medicine_name", "").strip()
            if not medicine_name:
                errors.append({"row": row_num, "error": "Missing medicine_name"})
                continue

            # Check if exists
            existing = await db.execute(
                select(MedicineInventory).where(
                    MedicineInventory.pharmacy_id == profile.id,
                    MedicineInventory.medicine_name == medicine_name,
                )
            )
            item = existing.scalar_one_or_none()

            if item:
                item.quantity_in_stock = int(row.get("quantity_in_stock", 0))
                item.price_per_unit = float(row["price_per_unit"]) if row.get("price_per_unit") else None
                item.generic_name = row.get("generic_name") or item.generic_name
                item.category = row.get("category") or item.category
                item.unit = row.get("unit") or item.unit
                item.requires_prescription = row.get("requires_prescription", "").lower() == "true"
                updated += 1
            else:
                new_item = MedicineInventory(
                    pharmacy_id=profile.id,
                    medicine_name=medicine_name,
                    generic_name=row.get("generic_name"),
                    category=row.get("category"),
                    quantity_in_stock=int(row.get("quantity_in_stock", 0)),
                    price_per_unit=float(row["price_per_unit"]) if row.get("price_per_unit") else None,
                    unit=row.get("unit"),
                    requires_prescription=row.get("requires_prescription", "").lower() == "true",
                )
                db.add(new_item)
                inserted += 1
        except Exception as e:
            errors.append({"row": row_num, "error": str(e)})

    await db.commit()
    return _success({
        "inserted": inserted,
        "updated": updated,
        "errors": errors[:50],
    }, f"Bulk upload complete: {inserted} inserted, {updated} updated")
