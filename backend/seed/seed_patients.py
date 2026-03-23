"""Seed 10 test patients with appointments and prescriptions."""
import asyncio, sys, os, random
from datetime import date, datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.doctor import DoctorProfile
from app.models.appointment import Appointment
from app.models.prescription import Prescription, PrescriptionItem
from app.services.auth_service import hash_password

PATIENTS = [
    {"name":"Ramesh Kumar","email":"ramesh.p@ss.dev","phone":"9300000001","dob":"1985-03-15","gender":"Male","blood":"B+","village":"Mohali","district":"SAS Nagar","state":"Punjab","allergies":["Penicillin"],"chronic":["Diabetes Type 2"],"ec_name":"Sita Kumar","ec_phone":"9300100001"},
    {"name":"Priyanka Devi","email":"priyanka.p@ss.dev","phone":"9300000002","dob":"1992-07-22","gender":"Female","blood":"O+","village":"Sangamner","district":"Ahmednagar","state":"Maharashtra","allergies":[],"chronic":[],"ec_name":"Vinod Devi","ec_phone":"9300100002"},
    {"name":"Subramaniam K","email":"subra.p@ss.dev","phone":"9300000003","dob":"1978-11-05","gender":"Male","blood":"A+","village":"Sivaganga","district":"Sivaganga","state":"Tamil Nadu","allergies":["Sulfa"],"chronic":["Hypertension"],"ec_name":"Lakshmi K","ec_phone":"9300100003"},
    {"name":"Fatima Begum","email":"fatima.p@ss.dev","phone":"9300000004","dob":"1990-01-12","gender":"Female","blood":"AB+","village":"Unnao","district":"Unnao","state":"Uttar Pradesh","allergies":[],"chronic":[],"ec_name":"Ahmed Khan","ec_phone":"9300100004"},
    {"name":"Gurpreet Singh","email":"gurpreet.p@ss.dev","phone":"9300000005","dob":"1960-09-30","gender":"Male","blood":"O-","village":"Bathinda","district":"Bathinda","state":"Punjab","allergies":["Aspirin"],"chronic":["Diabetes","Hypertension"],"ec_name":"Harjeet Kaur","ec_phone":"9300100005"},
    {"name":"Anita Joshi","email":"anita.p@ss.dev","phone":"9300000006","dob":"1988-04-18","gender":"Female","blood":"B-","village":"Sikar","district":"Sikar","state":"Rajasthan","allergies":[],"chronic":["Asthma"],"ec_name":"Mohan Joshi","ec_phone":"9300100006"},
    {"name":"Debashish Roy","email":"debashish.p@ss.dev","phone":"9300000007","dob":"1975-12-01","gender":"Male","blood":"A-","village":"Howrah","district":"Howrah","state":"West Bengal","allergies":[],"chronic":["Hypothyroidism"],"ec_name":"Sharmila Roy","ec_phone":"9300100007"},
    {"name":"Meenakshi S","email":"meenakshi.p@ss.dev","phone":"9300000008","dob":"1995-06-25","gender":"Female","blood":"O+","village":"Palakkad","district":"Palakkad","state":"Kerala","allergies":[],"chronic":[],"ec_name":"Suresh S","ec_phone":"9300100008"},
    {"name":"Rajendra Patel","email":"rajendra.p@ss.dev","phone":"9300000009","dob":"1970-08-14","gender":"Male","blood":"AB-","village":"Anand","district":"Anand","state":"Gujarat","allergies":["Ibuprofen"],"chronic":["Arthritis"],"ec_name":"Hema Patel","ec_phone":"9300100009"},
    {"name":"Lakshmi Reddy","email":"lakshmi.p@ss.dev","phone":"9300000010","dob":"1998-02-08","gender":"Female","blood":"B+","village":"Warangal","district":"Warangal","state":"Telangana","allergies":[],"chronic":[],"ec_name":"Venkat Reddy","ec_phone":"9300100010"},
]
PASSWORD = hash_password("patient123")
COMPLAINTS = ["Fever and body pain","Headache for 3 days","Stomach pain","Skin rash","Cough and cold","Joint pain"]
DIAGNOSES = ["Viral fever","Upper respiratory infection","Gastritis","Allergic dermatitis","Tension headache"]
SAMPLE_MEDS = [
    {"name":"Paracetamol 500mg","dosage":"1 tablet","frequency":"3 times/day","duration_days":5,"instructions":"After food"},
    {"name":"Amoxicillin 500mg","dosage":"1 capsule","frequency":"2 times/day","duration_days":7,"instructions":"After food"},
    {"name":"Cetirizine 10mg","dosage":"1 tablet","frequency":"Once at night","duration_days":5,"instructions":"Before sleep"},
    {"name":"Pantoprazole 40mg","dosage":"1 tablet","frequency":"Before breakfast","duration_days":14,"instructions":"Empty stomach"},
    {"name":"ORS Powder","dosage":"1 sachet/1L water","frequency":"As needed","duration_days":3,"instructions":"Sip throughout day"},
]

async def seed():
    async with AsyncSessionLocal() as db:
        docs = (await db.execute(select(DoctorProfile))).scalars().all()
        for pat in PATIENTS:
            if (await db.execute(select(User).where(User.email == pat["email"]))).scalar_one_or_none():
                continue
            user = User(email=pat["email"],phone=pat["phone"],password_hash=PASSWORD,role="patient",
                        full_name=pat["name"],preferred_language="hi",is_verified=True,is_active=True)
            db.add(user); await db.flush()
            profile = PatientProfile(user_id=user.id,date_of_birth=date.fromisoformat(pat["dob"]),
                gender=pat["gender"],blood_group=pat["blood"],village=pat["village"],district=pat["district"],
                state=pat["state"],allergies=pat["allergies"],chronic_conditions=pat["chronic"],
                emergency_contact_name=pat["ec_name"],emergency_contact_phone=pat["ec_phone"])
            db.add(profile); await db.flush()
            if docs:
                for a in range(random.randint(2,3)):
                    doc = random.choice(docs)
                    appt = Appointment(patient_id=profile.id,doctor_id=doc.id,
                        scheduled_at=datetime.now(timezone.utc)-timedelta(days=random.randint(5,60)),
                        status="completed",type="video",chief_complaint=random.choice(COMPLAINTS))
                    db.add(appt); await db.flush()
                    if a < 2:
                        meds = random.sample(SAMPLE_MEDS, k=random.randint(1,3))
                        rx = Prescription(appointment_id=appt.id,patient_id=profile.id,doctor_id=doc.id,
                            diagnosis=random.choice(DIAGNOSES),medicines=meds,advice="Rest well. Drink fluids.",
                            follow_up_date=date.today()+timedelta(days=random.randint(3,14)))
                        db.add(rx); await db.flush()
                        for med in meds:
                            db.add(PrescriptionItem(prescription_id=rx.id,medicine_name=med["name"],
                                dosage=med.get("dosage"),frequency=med.get("frequency"),
                                duration_days=med.get("duration_days"),instructions=med.get("instructions")))
        await db.commit()
        print(f"Seeded {len(PATIENTS)} patients with appointments and prescriptions.")

if __name__ == "__main__":
    asyncio.run(seed())
