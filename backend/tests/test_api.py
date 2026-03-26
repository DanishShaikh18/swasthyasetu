"""
SwasthyaSetu API — Full Test Suite
Run with: pytest tests/test_api.py -v
"""

import pytest
import httpx

BASE_URL = "http://localhost:8000"

# ── Shared state across tests ─────────────────────────────────────────────────
state = {
    "patient_token": None,
    "doctor_token": None,
    "pharmacy_token": None,
    "admin_token": None,
    "patient_id": None,
    "doctor_id": None,
    "doctor_profile_id": None,
    "pharmacy_id": None,
    "pharmacy_profile_id": None,
    "appointment_id": None,
    "prescription_id": None,
    "document_id": None,
    "inventory_item_id": None,
    "slot_template_id": None,
    "notification_id": None,
}


def headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── SYSTEM ────────────────────────────────────────────────────────────────────

def test_root():
    r = httpx.get(f"{BASE_URL}/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"
    print("✅ Root OK")


def test_health():
    r = httpx.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["checks"]["database"] == "ok"
    print(f"✅ Health OK — {data}")


# ── AUTH ──────────────────────────────────────────────────────────────────────

def test_register_patient():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "testpatient@swasthya.com",
        "phone": "9000000001",
        "password": "password123",
        "full_name": "Test Patient",
        "role": "patient",
        "preferred_language": "hi",
    })
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    state["patient_token"] = data["access_token"]
    state["patient_id"] = data["user_id"]
    print(f"✅ Patient registered — {data['user_id']}")


def test_register_doctor():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "testdoctor@swasthya.com",
        "phone": "9000000002",
        "password": "password123",
        "full_name": "Dr. Test Doctor",
        "role": "doctor",
        "preferred_language": "hi",
        "specialization": "General Physician",
        "qualification": "MBBS",
        "registration_number": "MH2024-99999",
        "experience_years": 5,
        "hospital_name": "Test Hospital",
        "bio": "Test doctor bio",
        "languages_spoken": ["Hindi", "English"],
    })
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    state["doctor_token"] = data["access_token"]
    state["doctor_id"] = data["user_id"]
    print(f"✅ Doctor registered — {data['user_id']}")


def test_register_pharmacy():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "testpharmacy@swasthya.com",
        "phone": "9000000003",
        "password": "password123",
        "full_name": "Test Pharmacist",
        "role": "pharmacy",
        "preferred_language": "hi",
        "pharmacy_name": "Test Pharmacy",
        "license_number": "MH-PHARM-2024-999",
        "address": "Shop 1, Test Road",
        "village": "Panvel",
        "district": "Raigad",
        "state": "Maharashtra",
        "latitude": 18.9894,
        "longitude": 73.1175,
        "pharmacy_phone": "9000000003",
    })
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    state["pharmacy_token"] = data["access_token"]
    state["pharmacy_id"] = data["user_id"]
    print(f"✅ Pharmacy registered — {data['user_id']}")


def test_login_patient():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "testpatient@swasthya.com",
        "password": "password123",
    })
    assert r.status_code == 200, r.text
    state["patient_token"] = r.json()["data"]["access_token"]
    print("✅ Patient login OK")


def test_login_doctor():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "testdoctor@swasthya.com",
        "password": "password123",
    })
    assert r.status_code == 200, r.text
    state["doctor_token"] = r.json()["data"]["access_token"]
    print("✅ Doctor login OK")


def test_login_admin():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "admin@swasthyasetu.com",
        "password": "adminpassword123",
    })
    assert r.status_code == 200, r.text
    state["admin_token"] = r.json()["data"]["access_token"]
    print("✅ Admin login OK")


def test_refresh_token():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/refresh")
    # Expects 401 since no cookie — just checking endpoint exists
    assert r.status_code in [200, 401, 422]
    print("✅ Refresh endpoint reachable")


# ── PATIENT ───────────────────────────────────────────────────────────────────

def test_get_patient_profile():
    r = httpx.get(f"{BASE_URL}/api/v1/patients/me",
                  headers=headers(state["patient_token"]))
    assert r.status_code == 200, r.text
    print("✅ Get patient profile OK")


def test_update_patient_profile():
    r = httpx.patch(f"{BASE_URL}/api/v1/patients/me",
                    headers=headers(state["patient_token"]),
                    json={
                        "full_name": "Test Patient Updated",
                        "blood_group": "O+",
                        "gender": "male",
                        "state": "Maharashtra",
                        "district": "Raigad",
                        "preferred_language": "hi",
                    })
    assert r.status_code == 200, r.text
    print("✅ Update patient profile OK")


def test_get_patient_prescriptions():
    r = httpx.get(f"{BASE_URL}/api/v1/patients/me/prescriptions",
                  headers=headers(state["patient_token"]),
                  params={"page": 1, "limit": 10})
    assert r.status_code == 200, r.text
    print("✅ Get patient prescriptions OK")


def test_get_patient_appointments():
    r = httpx.get(f"{BASE_URL}/api/v1/patients/me/appointments",
                  headers=headers(state["patient_token"]),
                  params={"page": 1, "limit": 10})
    assert r.status_code == 200, r.text
    print("✅ Get patient appointments OK")


def test_get_patient_documents():
    r = httpx.get(f"{BASE_URL}/api/v1/patients/me/documents",
                  headers=headers(state["patient_token"]))
    assert r.status_code == 200, r.text
    print("✅ Get patient documents OK")


def test_upload_patient_document():
    r = httpx.post(f"{BASE_URL}/api/v1/patients/me/documents",
                   headers=headers(state["patient_token"]),
                   json={
                       "file_url": "https://example.com/test.pdf",
                       "document_type": "lab_report",
                       "file_name": "test_report.pdf",
                       "file_size_kb": 100,
                       "notes": "Test document",
                   })
    assert r.status_code == 200, r.text
    print("✅ Upload document OK")


# ── DOCTOR (Public) ───────────────────────────────────────────────────────────

def test_list_doctors_public():
    r = httpx.get(f"{BASE_URL}/api/v1/doctors",
                  params={"page": 1, "limit": 10})
    assert r.status_code == 200, r.text
    print("✅ List doctors (public) OK")


def test_list_doctors_filtered():
    r = httpx.get(f"{BASE_URL}/api/v1/doctors",
                  params={"specialization": "General Physician", "state": "Maharashtra"})
    assert r.status_code == 200, r.text
    print("✅ List doctors filtered OK")


# ── ADMIN — Approve doctor & pharmacy ─────────────────────────────────────────

def test_admin_get_pending_doctors():
    r = httpx.get(f"{BASE_URL}/api/v1/admin/doctors/pending",
                  headers=headers(state["admin_token"]))
    assert r.status_code == 200, r.text
    doctors = r.json()["data"]
    if doctors:
        state["doctor_profile_id"] = doctors[0]["doctor_profile_id"]
        print(f"✅ Pending doctors — found {len(doctors)}, profile_id: {state['doctor_profile_id']}")
    else:
        print("✅ Pending doctors — none found (may already be approved)")


def test_admin_approve_doctor():
    if not state["doctor_profile_id"]:
        pytest.skip("No pending doctor profile id found")
    r = httpx.post(f"{BASE_URL}/api/v1/admin/doctors/{state['doctor_profile_id']}/approve",
                   headers=headers(state["admin_token"]))
    assert r.status_code == 200, r.text
    print(f"✅ Doctor approved — {state['doctor_profile_id']}")


def test_admin_get_pending_pharmacies():
    r = httpx.get(f"{BASE_URL}/api/v1/admin/pharmacy/pending",
                  headers=headers(state["admin_token"]))
    assert r.status_code == 200, r.text
    pharmacies = r.json()["data"]
    if pharmacies:
        state["pharmacy_profile_id"] = pharmacies[0]["pharmacy_profile_id"]
        print(f"✅ Pending pharmacies — found {len(pharmacies)}")
    else:
        print("✅ Pending pharmacies — none found")


def test_admin_approve_pharmacy():
    if not state["pharmacy_profile_id"]:
        pytest.skip("No pending pharmacy profile id found")
    r = httpx.post(f"{BASE_URL}/api/v1/admin/pharmacy/{state['pharmacy_profile_id']}/approve",
                   headers=headers(state["admin_token"]))
    assert r.status_code == 200, r.text
    print(f"✅ Pharmacy approved — {state['pharmacy_profile_id']}")


# ── DOCTOR (Authenticated) ────────────────────────────────────────────────────

def test_get_doctor_profile():
    r = httpx.get(f"{BASE_URL}/api/v1/doctors/me/profile",
                  headers=headers(state["doctor_token"]))
    assert r.status_code == 200, r.text
    print("✅ Get doctor profile OK")


def test_update_doctor_profile():
    r = httpx.patch(f"{BASE_URL}/api/v1/doctors/me/profile",
                    headers=headers(state["doctor_token"]),
                    json={
                        "consultation_fee": 300,
                        "bio": "Updated bio",
                        "hospital_name": "Updated Hospital",
                    })
    assert r.status_code == 200, r.text
    print("✅ Update doctor profile OK")


def test_toggle_doctor_availability():
    r = httpx.patch(f"{BASE_URL}/api/v1/doctors/me/availability",
                    headers=headers(state["doctor_token"]),
                    json={"is_available": True})
    assert r.status_code == 200, r.text
    print("✅ Toggle doctor availability OK")


def test_create_slot_template():
    r = httpx.post(f"{BASE_URL}/api/v1/doctors/me/slots",
                   headers=headers(state["doctor_token"]),
                   json={
                       "day_of_week": 4,
                       "start_time": "09:00:00",
                       "end_time": "13:00:00",
                       "slot_duration_min": 30,
                   })
    assert r.status_code == 200, r.text
    print("✅ Create slot template OK")


def test_get_slot_templates():
    r = httpx.get(f"{BASE_URL}/api/v1/doctors/me/slots",
                  headers=headers(state["doctor_token"]))
    assert r.status_code == 200, r.text
    print("✅ Get slot templates OK")


def test_get_doctor_appointments():
    r = httpx.get(f"{BASE_URL}/api/v1/doctors/me/appointments",
                  headers=headers(state["doctor_token"]),
                  params={"page": 1, "limit": 10})
    assert r.status_code == 200, r.text
    print("✅ Get doctor appointments OK")


def test_get_doctor_available_slots():
    r = httpx.get(f"{BASE_URL}/api/v1/doctors/{state['doctor_id']}/slots",
                  params={"days": 7})
    assert r.status_code == 200, r.text
    print("✅ Get available slots OK")


# ── APPOINTMENT ───────────────────────────────────────────────────────────────

def test_book_appointment():
    # Get available slots first
    r = httpx.get(f"{BASE_URL}/api/v1/doctors/{state['doctor_id']}/slots",
                  params={"days": 7})
    slots = r.json()
    slot_time = None

    # Try to find an available slot
    if isinstance(slots, dict) and slots.get("data"):
        for day in slots["data"]:
            if isinstance(day, dict) and day.get("slots"):
                slot_time = day["slots"][0].get("slot_time")
                break
    elif isinstance(slots, list) and slots:
        slot_time = slots[0].get("slot_time")

    if not slot_time:
        pytest.skip("No available slots found — create slot template first")

    r = httpx.post(f"{BASE_URL}/api/v1/patients/appointments",
                   headers=headers(state["patient_token"]),
                   json={
                       "doctor_id": state["doctor_id"],
                       "slot_time": slot_time,
                       "type": "video",
                       "chief_complaint": "Fever and headache",
                   })
    assert r.status_code == 200, r.text
    data = r.json()
    if data.get("data") and data["data"].get("id"):
        state["appointment_id"] = data["data"]["id"]
    print(f"✅ Book appointment OK — {state['appointment_id']}")


# ── PRESCRIPTION ──────────────────────────────────────────────────────────────

def test_write_prescription():
    r = httpx.post(f"{BASE_URL}/api/v1/doctors/me/prescriptions",
                   headers=headers(state["doctor_token"]),
                   json={
                       "patient_id": state["patient_id"],
                       "appointment_id": state["appointment_id"],
                       "diagnosis": "Viral fever",
                       "medicines": [
                           {"name": "Paracetamol", "dosage": "500mg",
                            "frequency": "TID", "duration": "5 days"}
                       ],
                       "advice": "Rest and drink fluids",
                       "follow_up_date": "2026-04-10",
                   })
    assert r.status_code == 200, r.text
    print("✅ Write prescription OK")


# ── PHARMACY ──────────────────────────────────────────────────────────────────

def test_search_pharmacies_public():
    r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/search",
                  params={"medicine": "Paracetamol", "in_stock": True})
    assert r.status_code == 200, r.text
    print("✅ Search pharmacies (public) OK")


def test_get_pharmacy_profile():
    r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/me/profile",
                  headers=headers(state["pharmacy_token"]))
    assert r.status_code == 200, r.text
    print("✅ Get pharmacy profile OK")


def test_update_pharmacy_profile():
    r = httpx.patch(f"{BASE_URL}/api/v1/pharmacy/me/profile",
                    headers=headers(state["pharmacy_token"]),
                    json={"pharmacy_name": "Updated Test Pharmacy", "state": "Maharashtra"})
    assert r.status_code == 200, r.text
    print("✅ Update pharmacy profile OK")


def test_toggle_pharmacy_status():
    r = httpx.patch(f"{BASE_URL}/api/v1/pharmacy/me/status",
                    headers=headers(state["pharmacy_token"]),
                    json={"is_open_now": True})
    assert r.status_code == 200, r.text
    print("✅ Toggle pharmacy status OK")


def test_add_inventory_item():
    r = httpx.post(f"{BASE_URL}/api/v1/pharmacy/me/inventory",
                   headers=headers(state["pharmacy_token"]),
                   json={
                       "medicine_name": "Paracetamol 500mg",
                       "generic_name": "Paracetamol",
                       "category": "Analgesic",
                       "quantity_in_stock": 100,
                       "price_per_unit": 2.5,
                       "unit": "tablet",
                       "requires_prescription": False,
                   })
    assert r.status_code == 200, r.text
    data = r.json()
    if data.get("data") and data["data"].get("id"):
        state["inventory_item_id"] = data["data"]["id"]
    print(f"✅ Add inventory item OK — {state['inventory_item_id']}")


def test_get_inventory():
    r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/me/inventory",
                  headers=headers(state["pharmacy_token"]),
                  params={"page": 1, "limit": 20})
    assert r.status_code == 200, r.text
    print("✅ Get inventory OK")


def test_update_inventory_item():
    if not state["inventory_item_id"]:
        pytest.skip("No inventory item id")
    r = httpx.patch(
        f"{BASE_URL}/api/v1/pharmacy/me/inventory/{state['inventory_item_id']}",
        headers=headers(state["pharmacy_token"]),
        json={"quantity_in_stock": 200, "price_per_unit": 3.0},
    )
    assert r.status_code == 200, r.text
    print("✅ Update inventory item OK")


# ── AI ────────────────────────────────────────────────────────────────────────

def test_ai_symptom_check():
    r = httpx.post(f"{BASE_URL}/api/v1/ai/symptoms",
                   headers=headers(state["patient_token"]),
                   json={
                       "symptoms": "I have fever, headache and body ache for 2 days",
                       "language": "en",
                   },
                   timeout=30.0)
    assert r.status_code == 200, r.text
    print("✅ AI symptom check OK")


# ── CONTENT ───────────────────────────────────────────────────────────────────

def test_get_daily_tip():
    r = httpx.get(f"{BASE_URL}/api/v1/content/daily-tip",
                  params={"language": "hi"})
    assert r.status_code == 200, r.text
    print("✅ Get daily tip OK")


def test_get_first_aid():
    r = httpx.get(f"{BASE_URL}/api/v1/content/first-aid",
                  params={"language": "hi"})
    assert r.status_code == 200, r.text
    print("✅ Get first aid OK")


def test_get_health_facts():
    r = httpx.get(f"{BASE_URL}/api/v1/content/health-facts",
                  params={"language": "hi"})
    assert r.status_code == 200, r.text
    print("✅ Get health facts OK")


def test_get_notifications():
    r = httpx.get(f"{BASE_URL}/api/v1/content/notifications/me",
                  headers=headers(state["patient_token"]),
                  params={"page": 1, "limit": 20})
    assert r.status_code == 200, r.text
    data = r.json()
    notifications = data.get("data", [])
    if notifications:
        state["notification_id"] = notifications[0].get("id")
    print(f"✅ Get notifications OK")


def test_mark_notification_read():
    if not state["notification_id"]:
        pytest.skip("No notification id found")
    r = httpx.patch(
        f"{BASE_URL}/api/v1/content/notifications/{state['notification_id']}/read",
        headers=headers(state["patient_token"]),
    )
    assert r.status_code == 200, r.text
    print("✅ Mark notification read OK")


# ── AUTH CLEANUP ──────────────────────────────────────────────────────────────

def test_logout():
    r = httpx.post(f"{BASE_URL}/api/v1/auth/logout",
                   headers=headers(state["patient_token"]))
    assert r.status_code == 200, r.text
    print("✅ Logout OK")