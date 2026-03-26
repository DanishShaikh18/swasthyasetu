"""Generate DoctorAvailableSlot entries from DoctorSlot weekly templates for next 30 days."""

import asyncio
import sys
import os
import uuid
from datetime import datetime, timedelta, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.doctor import DoctorSlot, DoctorAvailableSlot, DoctorProfile
from sqlalchemy import select


async def generate():
    async with AsyncSessionLocal() as db:
        doctors = (
            await db.execute(
                select(DoctorProfile).where(DoctorProfile.is_approved == True)
            )
        ).scalars().all()

        if not doctors:
            print("No approved doctors found.")
            return

        total_slots = 0
        for doctor in doctors:
            slots = (
                await db.execute(
                    select(DoctorSlot).where(
                        DoctorSlot.doctor_id == doctor.id,
                        DoctorSlot.is_active == True,
                    )
                )
            ).scalars().all()

            if not slots:
                # Create default slots if none exist (Mon-Fri 9:00-17:00)
                for day in range(5):
                    slot = DoctorSlot(
                        id=uuid.uuid4(),
                        doctor_id=doctor.id,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        slot_duration_min=15,
                        is_active=True,
                    )
                    db.add(slot)
                await db.flush()
                slots = (
                    await db.execute(
                        select(DoctorSlot).where(DoctorSlot.doctor_id == doctor.id)
                    )
                ).scalars().all()

            # Generate available slots for next 30 days
            now = datetime.now()
            doc_slot_count = 0
            for i in range(30):
                day = now + timedelta(days=i)
                for slot_template in slots:
                    if day.weekday() == slot_template.day_of_week:
                        start_t = (
                            slot_template.start_time
                            if isinstance(slot_template.start_time, time)
                            else datetime.strptime(
                                str(slot_template.start_time), "%H:%M:%S"
                            ).time()
                        )
                        end_t = (
                            slot_template.end_time
                            if isinstance(slot_template.end_time, time)
                            else datetime.strptime(
                                str(slot_template.end_time), "%H:%M:%S"
                            ).time()
                        )
                        start_dt = datetime.combine(day.date(), start_t)
                        end_dt = datetime.combine(day.date(), end_t)
                        current = start_dt
                        while current < end_dt:
                            existing = await db.execute(
                                select(DoctorAvailableSlot).where(
                                    DoctorAvailableSlot.doctor_id == doctor.id,
                                    DoctorAvailableSlot.slot_time == current,
                                )
                            )
                            if not existing.scalar():
                                available_slot = DoctorAvailableSlot(
                                    id=uuid.uuid4(),
                                    doctor_id=doctor.id,
                                    slot_time=current,
                                    status="available",
                                )
                                db.add(available_slot)
                                doc_slot_count += 1
                            current += timedelta(
                                minutes=slot_template.slot_duration_min
                            )

            await db.commit()
            total_slots += doc_slot_count
            print(f"  Generated {doc_slot_count} slots for doctor {doctor.id}")

        print(f"\nTotal: {total_slots} available slots generated for {len(doctors)} doctors.")


if __name__ == "__main__":
    asyncio.run(generate())
