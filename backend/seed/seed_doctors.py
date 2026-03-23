"""Seed 20 doctors across 8 specializations and Indian states."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.doctor import DoctorProfile, DoctorSlot
from app.services.auth_service import hash_password
from datetime import time


DOCTORS = [
    # General Physicians (5)
    {"name": "Dr. Rajesh Sharma", "email": "rajesh.sharma@ss.dev", "phone": "9100000001",
     "spec": "General Physician", "qual": "MBBS, MD (General Medicine)",
     "reg": "DMC-2015-1234", "exp": 12, "langs": ["hi", "en", "pa"],
     "fee": 0, "hospital": "PHC Amritsar", "bio": "Experienced general physician serving rural Punjab for over a decade.",
     "state": "Punjab"},
    {"name": "Dr. Priya Deshmukh", "email": "priya.deshmukh@ss.dev", "phone": "9100000002",
     "spec": "General Physician", "qual": "MBBS, DNB (Family Medicine)",
     "reg": "MMC-2017-5678", "exp": 8, "langs": ["mr", "hi", "en"],
     "fee": 200, "hospital": "District Hospital Pune", "bio": "Family medicine specialist with focus on preventive healthcare.",
     "state": "Maharashtra"},
    {"name": "Dr. Kavitha Rajan", "email": "kavitha.rajan@ss.dev", "phone": "9100000003",
     "spec": "General Physician", "qual": "MBBS",
     "reg": "TNMC-2019-9012", "exp": 6, "langs": ["ta", "en"],
     "fee": 150, "hospital": "GH Madurai", "bio": "Dedicated to providing quality healthcare in Tamil Nadu's rural areas.",
     "state": "Tamil Nadu"},
    {"name": "Dr. Arun Kumar Singh", "email": "arun.singh@ss.dev", "phone": "9100000004",
     "spec": "General Physician", "qual": "MBBS, MD",
     "reg": "UPMC-2014-3456", "exp": 13, "langs": ["hi", "en"],
     "fee": 0, "hospital": "CHC Lucknow", "bio": "Government physician committed to rural health in Uttar Pradesh.",
     "state": "Uttar Pradesh"},
    {"name": "Dr. Suman Das", "email": "suman.das@ss.dev", "phone": "9100000005",
     "spec": "General Physician", "qual": "MBBS",
     "reg": "WBMC-2020-7890", "exp": 5, "langs": ["hi", "en"],
     "fee": 100, "hospital": "Rural Clinic Kolkata", "bio": "Young physician passionate about digital health for underserved communities.",
     "state": "West Bengal"},
    # Pediatricians (3)
    {"name": "Dr. Meena Gupta", "email": "meena.gupta@ss.dev", "phone": "9100000006",
     "spec": "Pediatrician", "qual": "MBBS, MD (Pediatrics)",
     "reg": "RMC-2016-1111", "exp": 10, "langs": ["hi", "en"],
     "fee": 300, "hospital": "Children's Hospital Jaipur", "bio": "Child specialist with expertise in nutrition and immunization.",
     "state": "Rajasthan"},
    {"name": "Dr. Lakshmi Nair", "email": "lakshmi.nair@ss.dev", "phone": "9100000007",
     "spec": "Pediatrician", "qual": "MBBS, DCH",
     "reg": "KMC-2018-2222", "exp": 7, "langs": ["ml", "en", "ta"],
     "fee": 250, "hospital": "Govt. Hospital Kochi", "bio": "Pediatrician focusing on neonatal care and childhood development.",
     "state": "Kerala"},
    {"name": "Dr. Vikram Patel", "email": "vikram.patel@ss.dev", "phone": "9100000008",
     "spec": "Pediatrician", "qual": "MBBS, MD (Pediatrics)",
     "reg": "GMC-2015-3333", "exp": 11, "langs": ["gu", "hi", "en"],
     "fee": 0, "hospital": "Civil Hospital Ahmedabad", "bio": "Government pediatrician devoted to child health in Gujarat.",
     "state": "Gujarat"},
    # Cardiologists (3)
    {"name": "Dr. Suresh Reddy", "email": "suresh.reddy@ss.dev", "phone": "9100000009",
     "spec": "Cardiologist", "qual": "MBBS, MD, DM (Cardiology)",
     "reg": "APMC-2012-4444", "exp": 15, "langs": ["te", "en", "hi"],
     "fee": 500, "hospital": "Heart Care Center Hyderabad", "bio": "Senior cardiologist with 15+ years of experience in interventional cardiology.",
     "state": "Telangana"},
    {"name": "Dr. Anjali Mehta", "email": "anjali.mehta@ss.dev", "phone": "9100000010",
     "spec": "Cardiologist", "qual": "MBBS, MD, DM (Cardiology)",
     "reg": "MMC-2013-5555", "exp": 14, "langs": ["mr", "hi", "en"],
     "fee": 450, "hospital": "Lilavati Hospital Mumbai", "bio": "Preventive cardiology specialist focused on rural heart health awareness.",
     "state": "Maharashtra"},
    {"name": "Dr. Harpreet Kaur", "email": "harpreet.kaur@ss.dev", "phone": "9100000011",
     "spec": "Cardiologist", "qual": "MBBS, DM (Cardiology)",
     "reg": "PMC-2014-6666", "exp": 13, "langs": ["pa", "hi", "en"],
     "fee": 400, "hospital": "PGIMER Chandigarh", "bio": "Academic cardiologist with research focus on lifestyle diseases in Punjab.",
     "state": "Punjab"},
    # Dermatologists (2)
    {"name": "Dr. Neha Joshi", "email": "neha.joshi@ss.dev", "phone": "9100000012",
     "spec": "Dermatologist", "qual": "MBBS, MD (Dermatology)",
     "reg": "RMC-2017-7777", "exp": 8, "langs": ["hi", "en"],
     "fee": 350, "hospital": "Skin Care Clinic Jaipur", "bio": "Dermatologist specializing in tropical skin conditions common in rural India.",
     "state": "Rajasthan"},
    {"name": "Dr. Ramesh Iyer", "email": "ramesh.iyer@ss.dev", "phone": "9100000013",
     "spec": "Dermatologist", "qual": "MBBS, DVD",
     "reg": "KMC-2016-8888", "exp": 9, "langs": ["kn", "en", "hi"],
     "fee": 300, "hospital": "Victoria Hospital Bangalore", "bio": "Expert in occupational dermatology and sun-related skin conditions.",
     "state": "Karnataka"},
    # Gynecologists (2)
    {"name": "Dr. Sunita Yadav", "email": "sunita.yadav@ss.dev", "phone": "9100000014",
     "spec": "Gynecologist", "qual": "MBBS, MS (OBG)",
     "reg": "UPMC-2015-9999", "exp": 11, "langs": ["hi", "en"],
     "fee": 0, "hospital": "District Women's Hospital Varanasi", "bio": "Dedicated to maternal health in rural UP. Specializes in high-risk pregnancies.",
     "state": "Uttar Pradesh"},
    {"name": "Dr. Deepa Krishnan", "email": "deepa.krishnan@ss.dev", "phone": "9100000015",
     "spec": "Gynecologist", "qual": "MBBS, DGO",
     "reg": "TNMC-2016-1010", "exp": 10, "langs": ["ta", "en"],
     "fee": 400, "hospital": "Apollo Clinic Chennai", "bio": "Women's health specialist with focus on reproductive health education.",
     "state": "Tamil Nadu"},
    # Orthopedics (2)
    {"name": "Dr. Manoj Tiwari", "email": "manoj.tiwari@ss.dev", "phone": "9100000016",
     "spec": "Orthopedic Surgeon", "qual": "MBBS, MS (Ortho)",
     "reg": "MPMC-2013-1111", "exp": 14, "langs": ["hi", "en"],
     "fee": 350, "hospital": "Bone & Joint Hospital Bhopal", "bio": "Orthopedic surgeon experienced in treating farming-related musculoskeletal injuries.",
     "state": "Madhya Pradesh"},
    {"name": "Dr. Ravi Shankar", "email": "ravi.shankar@ss.dev", "phone": "9100000017",
     "spec": "Orthopedic Surgeon", "qual": "MBBS, DNB (Ortho)",
     "reg": "WBMC-2015-1212", "exp": 11, "langs": ["hi", "en"],
     "fee": 400, "hospital": "SSKM Hospital Kolkata", "bio": "Experienced orthopedist specializing in trauma and sports injuries.",
     "state": "West Bengal"},
    # Psychiatrist (1)
    {"name": "Dr. Ananya Bose", "email": "ananya.bose@ss.dev", "phone": "9100000018",
     "spec": "Psychiatrist", "qual": "MBBS, MD (Psychiatry)",
     "reg": "WBMC-2016-1313", "exp": 9, "langs": ["hi", "en"],
     "fee": 500, "hospital": "NIMHANS Kolkata", "bio": "Mental health advocate focusing on reducing stigma in rural communities.",
     "state": "West Bengal"},
    # ENT (1)
    {"name": "Dr. Kiran Patil", "email": "kiran.patil@ss.dev", "phone": "9100000019",
     "spec": "ENT Specialist", "qual": "MBBS, MS (ENT)",
     "reg": "KMC-2018-1414", "exp": 7, "langs": ["kn", "hi", "en"],
     "fee": 250, "hospital": "SDM Hospital Dharwad", "bio": "ENT specialist with experience in managing hearing disorders in rural Karnataka.",
     "state": "Karnataka"},
    # Ophthalmologist (1)
    {"name": "Dr. Pooja Agarwal", "email": "pooja.agarwal@ss.dev", "phone": "9100000020",
     "spec": "Ophthalmologist", "qual": "MBBS, MS (Ophthalmology)",
     "reg": "RMC-2017-1515", "exp": 8, "langs": ["hi", "en"],
     "fee": 300, "hospital": "Eye Care Centre Jodhpur", "bio": "Eye specialist conducting free cataract camps in rural Rajasthan.",
     "state": "Rajasthan"},
]

PASSWORD = hash_password("doctor123")


async def seed():
    async with AsyncSessionLocal() as db:
        for doc in DOCTORS:
            existing = await db.execute(
                __import__("sqlalchemy").select(User).where(User.email == doc["email"])
            )
            if existing.scalar_one_or_none():
                continue

            user = User(
                email=doc["email"], phone=doc["phone"],
                password_hash=PASSWORD, role="doctor",
                full_name=doc["name"], preferred_language=doc["langs"][0],
                is_verified=True, is_active=True,
            )
            db.add(user)
            await db.flush()

            profile = DoctorProfile(
                user_id=user.id,
                specialization=doc["spec"],
                qualification=doc["qual"],
                registration_number=doc["reg"],
                experience_years=doc["exp"],
                languages_spoken=doc["langs"],
                consultation_fee=doc["fee"],
                is_available=True,
                hospital_name=doc["hospital"],
                bio=doc["bio"],
                is_approved=True,
            )
            db.add(profile)
            await db.flush()

            # Add default weekly slots (Mon-Fri 9:00-17:00)
            for day in range(5):
                slot = DoctorSlot(
                    doctor_id=profile.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    slot_duration_min=15,
                )
                db.add(slot)

        await db.commit()
        print(f"Seeded {len(DOCTORS)} doctors with weekly slot templates.")


if __name__ == "__main__":
    asyncio.run(seed())
