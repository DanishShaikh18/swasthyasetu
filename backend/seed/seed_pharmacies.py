"""Seed 15 pharmacies with PostGIS locations and medicine inventory."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.pharmacy import PharmacyProfile, MedicineInventory
from app.services.auth_service import hash_password
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

PHARMACIES = [
    # Punjab (3)
    {"name": "Sharma Medical Store", "email": "sharma.meds@ss.dev", "phone": "9200000001",
     "address": "Main Market, Amritsar, Punjab", "village": "Amritsar", "district": "Amritsar", "state": "Punjab",
     "lat": 31.6340, "lng": 74.8723},
    {"name": "Guru Nanak Pharmacy", "email": "gurunanak.pharma@ss.dev", "phone": "9200000002",
     "address": "GT Road, Ludhiana, Punjab", "village": "Ludhiana", "district": "Ludhiana", "state": "Punjab",
     "lat": 30.9010, "lng": 75.8573},
    {"name": "Punjab Health Chemist", "email": "punjab.health@ss.dev", "phone": "9200000003",
     "address": "Bus Stand Road, Patiala, Punjab", "village": "Patiala", "district": "Patiala", "state": "Punjab",
     "lat": 30.3398, "lng": 76.3869},
    # Maharashtra (2)
    {"name": "Deshmukh Aushadhi", "email": "deshmukh.pharma@ss.dev", "phone": "9200000004",
     "address": "Station Road, Pune, Maharashtra", "village": "Pune", "district": "Pune", "state": "Maharashtra",
     "lat": 18.5204, "lng": 73.8567},
    {"name": "Shivaji Medical", "email": "shivaji.meds@ss.dev", "phone": "9200000005",
     "address": "Mahatma Phule Road, Nashik, Maharashtra", "village": "Nashik", "district": "Nashik", "state": "Maharashtra",
     "lat": 20.0063, "lng": 73.7900},
    # Tamil Nadu (2)
    {"name": "Murugan Pharmacy", "email": "murugan.pharma@ss.dev", "phone": "9200000006",
     "address": "East Masi Street, Madurai, Tamil Nadu", "village": "Madurai", "district": "Madurai", "state": "Tamil Nadu",
     "lat": 9.9252, "lng": 78.1198},
    {"name": "Chennai Med Centre", "email": "chennai.med@ss.dev", "phone": "9200000007",
     "address": "Anna Nagar, Chennai, Tamil Nadu", "village": "Chennai", "district": "Chennai", "state": "Tamil Nadu",
     "lat": 13.0827, "lng": 80.2707},
    # UP (2)
    {"name": "Verma Medical Hall", "email": "verma.meds@ss.dev", "phone": "9200000008",
     "address": "Chowk, Lucknow, Uttar Pradesh", "village": "Lucknow", "district": "Lucknow", "state": "Uttar Pradesh",
     "lat": 26.8467, "lng": 80.9462},
    {"name": "Ganga Pharmacy", "email": "ganga.pharma@ss.dev", "phone": "9200000009",
     "address": "Dashashwamedh Road, Varanasi, UP", "village": "Varanasi", "district": "Varanasi", "state": "Uttar Pradesh",
     "lat": 25.3176, "lng": 82.9739},
    # Rajasthan (2)
    {"name": "Rajasthan Medical Store", "email": "raj.meds@ss.dev", "phone": "9200000010",
     "address": "MI Road, Jaipur, Rajasthan", "village": "Jaipur", "district": "Jaipur", "state": "Rajasthan",
     "lat": 26.9124, "lng": 75.7873},
    {"name": "Jodhpur Chemist", "email": "jodhpur.chem@ss.dev", "phone": "9200000011",
     "address": "Nai Sarak, Jodhpur, Rajasthan", "village": "Jodhpur", "district": "Jodhpur", "state": "Rajasthan",
     "lat": 26.2389, "lng": 73.0243},
    # West Bengal (2)
    {"name": "Bose Medical", "email": "bose.meds@ss.dev", "phone": "9200000012",
     "address": "Park Street, Kolkata, West Bengal", "village": "Kolkata", "district": "Kolkata", "state": "West Bengal",
     "lat": 22.5726, "lng": 88.3639},
    {"name": "Bengal Pharmacy", "email": "bengal.pharma@ss.dev", "phone": "9200000013",
     "address": "College Street, Kolkata, West Bengal", "village": "Kolkata", "district": "Kolkata", "state": "West Bengal",
     "lat": 22.5744, "lng": 88.3629},
    # Kerala (1)
    {"name": "Kerala Ayur Medicals", "email": "kerala.ayur@ss.dev", "phone": "9200000014",
     "address": "MG Road, Kochi, Kerala", "village": "Kochi", "district": "Ernakulam", "state": "Kerala",
     "lat": 9.9312, "lng": 76.2673},
    # Gujarat (1)
    {"name": "Gujarat Health Pharmacy", "email": "guj.health@ss.dev", "phone": "9200000015",
     "address": "CG Road, Ahmedabad, Gujarat", "village": "Ahmedabad", "district": "Ahmedabad", "state": "Gujarat",
     "lat": 23.0225, "lng": 72.5714},
]

MEDICINES = [
    # Common antibiotics (requires_prescription=True)
    {"name": "Amoxicillin 500mg", "generic": "Amoxicillin", "cat": "Antibiotic", "qty": 200, "price": 8.50, "unit": "capsule", "rx": True},
    {"name": "Azithromycin 500mg", "generic": "Azithromycin", "cat": "Antibiotic", "qty": 150, "price": 15.00, "unit": "tablet", "rx": True},
    {"name": "Ciprofloxacin 500mg", "generic": "Ciprofloxacin", "cat": "Antibiotic", "qty": 180, "price": 12.00, "unit": "tablet", "rx": True},
    {"name": "Metronidazole 400mg", "generic": "Metronidazole", "cat": "Antibiotic", "qty": 300, "price": 5.00, "unit": "tablet", "rx": True},
    {"name": "Doxycycline 100mg", "generic": "Doxycycline", "cat": "Antibiotic", "qty": 120, "price": 10.00, "unit": "capsule", "rx": True},
    # Painkillers
    {"name": "Paracetamol 500mg", "generic": "Acetaminophen", "cat": "Analgesic", "qty": 500, "price": 2.00, "unit": "tablet", "rx": False},
    {"name": "Ibuprofen 400mg", "generic": "Ibuprofen", "cat": "NSAID", "qty": 300, "price": 5.00, "unit": "tablet", "rx": False},
    {"name": "Diclofenac 50mg", "generic": "Diclofenac", "cat": "NSAID", "qty": 250, "price": 4.50, "unit": "tablet", "rx": False},
    {"name": "Combiflam", "generic": "Ibuprofen+Paracetamol", "cat": "Analgesic", "qty": 200, "price": 6.00, "unit": "tablet", "rx": False},
    # Antidiabetics
    {"name": "Metformin 500mg", "generic": "Metformin", "cat": "Antidiabetic", "qty": 400, "price": 3.50, "unit": "tablet", "rx": True},
    {"name": "Glimepiride 2mg", "generic": "Glimepiride", "cat": "Antidiabetic", "qty": 200, "price": 8.00, "unit": "tablet", "rx": True},
    {"name": "Insulin Glargine", "generic": "Insulin", "cat": "Antidiabetic", "qty": 50, "price": 450.00, "unit": "vial", "rx": True},
    # Antihypertensives
    {"name": "Amlodipine 5mg", "generic": "Amlodipine", "cat": "Antihypertensive", "qty": 350, "price": 4.00, "unit": "tablet", "rx": True},
    {"name": "Telmisartan 40mg", "generic": "Telmisartan", "cat": "Antihypertensive", "qty": 300, "price": 7.00, "unit": "tablet", "rx": True},
    {"name": "Atenolol 50mg", "generic": "Atenolol", "cat": "Antihypertensive", "qty": 250, "price": 5.00, "unit": "tablet", "rx": True},
    # ORS & Rehydration
    {"name": "ORS Powder", "generic": "Oral Rehydration Salt", "cat": "Rehydration", "qty": 500, "price": 10.00, "unit": "sachet", "rx": False},
    {"name": "Electral Powder", "generic": "Electrolyte Solution", "cat": "Rehydration", "qty": 300, "price": 15.00, "unit": "sachet", "rx": False},
    # Vitamins & Supplements
    {"name": "Vitamin D3 60K IU", "generic": "Cholecalciferol", "cat": "Vitamin", "qty": 200, "price": 30.00, "unit": "capsule", "rx": False},
    {"name": "Iron + Folic Acid", "generic": "Ferrous Sulphate + Folic Acid", "cat": "Supplement", "qty": 400, "price": 3.00, "unit": "tablet", "rx": False},
    {"name": "Calcium + Vitamin D", "generic": "Calcium Carbonate", "cat": "Supplement", "qty": 300, "price": 5.00, "unit": "tablet", "rx": False},
    {"name": "Multivitamin", "generic": "Multivitamin Complex", "cat": "Supplement", "qty": 250, "price": 8.00, "unit": "tablet", "rx": False},
    {"name": "B-Complex", "generic": "Vitamin B Complex", "cat": "Vitamin", "qty": 350, "price": 4.00, "unit": "tablet", "rx": False},
    # Common medicines
    {"name": "Cetirizine 10mg", "generic": "Cetirizine", "cat": "Antihistamine", "qty": 400, "price": 3.00, "unit": "tablet", "rx": False},
    {"name": "Pantoprazole 40mg", "generic": "Pantoprazole", "cat": "Antacid", "qty": 300, "price": 6.00, "unit": "tablet", "rx": False},
    {"name": "Domperidone 10mg", "generic": "Domperidone", "cat": "Antiemetic", "qty": 250, "price": 4.00, "unit": "tablet", "rx": False},
    {"name": "Loperamide 2mg", "generic": "Loperamide", "cat": "Antidiarrheal", "qty": 200, "price": 5.00, "unit": "capsule", "rx": False},
    {"name": "Salbutamol Inhaler", "generic": "Salbutamol", "cat": "Bronchodilator", "qty": 80, "price": 120.00, "unit": "inhaler", "rx": True},
    {"name": "Montelukast 10mg", "generic": "Montelukast", "cat": "Anti-asthmatic", "qty": 150, "price": 10.00, "unit": "tablet", "rx": True},
    {"name": "Cough Syrup", "generic": "Dextromethorphan", "cat": "Cough/Cold", "qty": 200, "price": 65.00, "unit": "bottle", "rx": False},
    {"name": "Betadine Solution", "generic": "Povidone-Iodine", "cat": "Antiseptic", "qty": 150, "price": 55.00, "unit": "bottle", "rx": False},
    {"name": "Dettol Antiseptic", "generic": "Chloroxylenol", "cat": "Antiseptic", "qty": 200, "price": 45.00, "unit": "bottle", "rx": False},
    {"name": "Bandage Roll", "generic": "Cotton Bandage", "cat": "First Aid", "qty": 500, "price": 25.00, "unit": "roll", "rx": False},
    {"name": "Cotton Roll 100g", "generic": "Absorbent Cotton", "cat": "First Aid", "qty": 300, "price": 35.00, "unit": "pack", "rx": False},
    {"name": "Ranitidine 150mg", "generic": "Ranitidine", "cat": "Antacid", "qty": 280, "price": 4.00, "unit": "tablet", "rx": False},
    {"name": "Omeprazole 20mg", "generic": "Omeprazole", "cat": "Antacid", "qty": 320, "price": 5.50, "unit": "capsule", "rx": False},
    {"name": "Albendazole 400mg", "generic": "Albendazole", "cat": "Anthelmintic", "qty": 200, "price": 8.00, "unit": "tablet", "rx": False},
    {"name": "Chloroquine 250mg", "generic": "Chloroquine", "cat": "Antimalarial", "qty": 100, "price": 12.00, "unit": "tablet", "rx": True},
    {"name": "Artemether Combo", "generic": "Artemether+Lumefantrine", "cat": "Antimalarial", "qty": 80, "price": 45.00, "unit": "tablet", "rx": True},
    {"name": "Zinc Tablets 20mg", "generic": "Zinc Sulphate", "cat": "Supplement", "qty": 400, "price": 3.00, "unit": "tablet", "rx": False},
    {"name": "Povidone Eye Drops", "generic": "Polyvinyl Alcohol", "cat": "Ophthalmic", "qty": 100, "price": 40.00, "unit": "bottle", "rx": False},
]

PASSWORD = hash_password("pharmacy123")


async def seed():
    async with AsyncSessionLocal() as db:
        for ph in PHARMACIES:
            existing = await db.execute(select(User).where(User.email == ph["email"]))
            if existing.scalar_one_or_none():
                continue

            user = User(
                email=ph["email"], phone=ph["phone"],
                password_hash=PASSWORD, role="pharmacy",
                full_name=ph["name"], preferred_language="hi",
                is_verified=True, is_active=True,
            )
            db.add(user)
            await db.flush()

            location = WKTElement(f"POINT({ph['lng']} {ph['lat']})", srid=4326)
            profile = PharmacyProfile(
                user_id=user.id,
                pharmacy_name=ph["name"],
                license_number=f"PH-{ph['state'][:2].upper()}-{ph['phone'][-4:]}",
                address=ph["address"],
                village=ph["village"],
                district=ph["district"],
                state=ph["state"],
                location=location,
                phone=ph["phone"],
                opening_hours={"mon_fri": "8:00-21:00", "sat": "8:00-18:00", "sun": "9:00-14:00"},
                is_approved=True,
                is_open_now=True,
            )
            db.add(profile)
            await db.flush()

            # Add medicines — vary quantities slightly per pharmacy
            import random
            num_meds = random.randint(40, len(MEDICINES))
            selected_meds = random.sample(MEDICINES, num_meds)
            for med in selected_meds:
                qty_var = random.randint(-int(med["qty"] * 0.3), int(med["qty"] * 0.3))
                item = MedicineInventory(
                    pharmacy_id=profile.id,
                    medicine_name=med["name"],
                    generic_name=med["generic"],
                    category=med["cat"],
                    quantity_in_stock=max(0, med["qty"] + qty_var),
                    price_per_unit=med["price"],
                    unit=med["unit"],
                    requires_prescription=med["rx"],
                )
                db.add(item)

        await db.commit()
        print(f"Seeded {len(PHARMACIES)} pharmacies with medicine inventory.")


if __name__ == "__main__":
    asyncio.run(seed())
