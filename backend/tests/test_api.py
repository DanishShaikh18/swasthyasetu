"""
SwasthyaSetu API — Full Test Suite
Run with: pytest tests/test_api.py -v -s

Fix applied: doctor_id (and other IDs) are now resolved from /doctors/me/profile
inside the slot test itself, so state["doctor_id"] = None never causes a 422.
All tests are ordered explicitly via pytest-ordering (pip install pytest-ordering)
or simply run top-to-bottom, which pytest does by default in a single file.
"""

import pytest
import httpx

BASE_URL = "http://localhost:8000"

# ── Shared mutable state (populated as tests run in order) ────────────────────
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
    "inventory_item_id": None,
    "notification_id": None,
    "_first_slot_time": None,
    "patient_profile_id": None,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def auth(token: str) -> dict:
    """Return Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


def resolve_doctor_id() -> str:
    """
    Return doctor_id from state if already set, otherwise fetch it live
    from /doctors/me/profile so tests never send `None` as a path param.
    Raises pytest.skip if the doctor is not yet logged in.
    """
    if state["doctor_id"]:
        return state["doctor_id"]

    token = state.get("doctor_token")
    if not token:
        pytest.skip("Doctor token not available — run login tests first")

    r = httpx.get(f"{BASE_URL}/api/v1/doctors/me/profile", headers=auth(token))
    if r.status_code != 200:
        pytest.skip(f"Could not fetch doctor profile: {r.text}")

    data = r.json().get("data", {})
    doctor_id = data.get("user_id") or data.get("id")
    if not doctor_id:
        pytest.skip("doctor_id not found in /doctors/me/profile response")

    state["doctor_id"] = doctor_id
    return doctor_id


# ═════════════════════════════════════════════════════════════════════════════
# SYSTEM
# ═════════════════════════════════════════════════════════════════════════════

class TestSystem:

    def test_root(self):
        r = httpx.get(f"{BASE_URL}/")
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "running"
        print("✅ Root OK")

    def test_health(self):
        r = httpx.get(f"{BASE_URL}/health")
        assert r.status_code == 200, r.text
        assert r.json()["checks"]["database"] == "ok"
        print("✅ Health OK")


# ═════════════════════════════════════════════════════════════════════════════
# AUTH — REGISTER
# ═════════════════════════════════════════════════════════════════════════════

class TestAuthRegister:

    def test_register_patient(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
            "email": "aarav.sharma.test2026@gmail.com",
            "phone": "9810001122",
            "password": "Test@1234",
            "full_name": "Aarav Sharma",
            "role": "patient",
            "preferred_language": "hi",
        })
        assert r.status_code == 200, r.text

        data = r.json()["data"]
        state["patient_token"] = data["access_token"]
        state["patient_id"] = data["user_id"]

        print(f"✅ Patient registered — {data['user_id']}")

    def test_register_doctor(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
            "email": "dr.kavya.nair.test2026@gmail.com",
            "phone": "9810002233",
            "password": "Test@1234",
            "full_name": "Dr. Kavya Nair",
            "role": "doctor",
            "preferred_language": "en",
            "specialization": "General Physician",
            "qualification": "MBBS MD",
            "registration_number": "MH2026-77889",
            "experience_years": 11,
            "hospital_name": "Sunrise Health Clinic",
            "bio": "Focused on preventive healthcare and rural outreach",
            "languages_spoken": ["English", "Hindi", "Malayalam"],
        })
        assert r.status_code == 200, r.text

        data = r.json()["data"]
        state["doctor_token"] = data["access_token"]
        state["doctor_id"] = data["user_id"]

        print(f"✅ Doctor registered — {data['user_id']}")

    def test_register_pharmacy(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
            "email": "raj.medicals.test2026@gmail.com",
            "phone": "9810003344",
            "password": "Test@1234",
            "full_name": "Rajesh Patel",
            "role": "pharmacy",
            "preferred_language": "hi",
            "pharmacy_name": "Raj Medical Store",
            "license_number": "GJ-PHARM-2026-5566",
            "address": "Main Road, Near Bus Stand",
            "village": "Surat",
            "district": "Surat",
            "state": "Gujarat",
            "latitude": 21.1702,
            "longitude": 72.8311,
            "pharmacy_phone": "9810003344",
        })
        assert r.status_code == 200, r.text

        data = r.json()["data"]
        state["pharmacy_token"] = data["access_token"]
        state["pharmacy_id"] = data["user_id"]

        print(f"✅ Pharmacy registered — {data['user_id']}")


# ═════════════════════════════════════════════════════════════════════════════
# AUTH — LOGIN
# ═════════════════════════════════════════════════════════════════════════════

class TestAuthLogin:

    def test_login_patient(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": "aarav.sharma.test2026@gmail.com",
            "password": "Test@1234",
        })
        assert r.status_code == 200, r.text

        data = r.json()["data"]
        state["patient_token"] = data["access_token"]

        if not state["patient_id"]:
            state["patient_id"] = data.get("user_id")

        print("✅ Patient login OK")

    def test_login_doctor(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": "dr.kavya.nair.test2026@gmail.com",
            "password": "Test@1234",
        })
        assert r.status_code == 200, r.text

        data = r.json()["data"]
        state["doctor_token"] = data["access_token"]

        if not state["doctor_id"]:
            state["doctor_id"] = data.get("user_id")

        print("✅ Doctor login OK")

    def test_login_pharmacy(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": "raj.medicals.test2026@gmail.com",
            "password": "Test@1234",
        })
        assert r.status_code == 200, r.text

        data = r.json()["data"]
        state["pharmacy_token"] = data["access_token"]

        if not state["pharmacy_id"]:
            state["pharmacy_id"] = data.get("user_id")

        print("✅ Pharmacy login OK")

    def test_login_admin(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": "admin@swasthyasetu.com",
            "password": "adminpassword123",
        })
        assert r.status_code == 200, r.text
        state["admin_token"] = r.json()["data"]["access_token"]
        print("✅ Admin login OK")

    def test_refresh_token_endpoint_reachable(self):
        """Refresh without a cookie/body — expect 200, 401, or 422 (all valid)."""
        r = httpx.post(f"{BASE_URL}/api/v1/auth/refresh")
        assert r.status_code in [200, 401, 422], r.text
        print("✅ Refresh endpoint reachable")

# ═════════════════════════════════════════════════════════════════════════════
# PATIENT
# ═════════════════════════════════════════════════════════════════════════════

class TestPatient:

    def test_get_patient_profile(self):
        r = httpx.get(f"{BASE_URL}/api/v1/patients/me",
                      headers=auth(state["patient_token"]))
        assert r.status_code == 200, r.text
        data = r.json().get("data", {})
        # Capture patient_profile_id (internal DB id, different from user_id)
        state["patient_profile_id"] = data.get("id") or data.get("profile_id")
        print(f"✅ Get patient profile OK — profile_id: {state['patient_profile_id']}")

    def test_update_patient_profile(self):
        r = httpx.patch(f"{BASE_URL}/api/v1/patients/me",
                        headers=auth(state["patient_token"]),
                        json={
                            "full_name": "Arjun Sharma",
                            "blood_group": "A+",
                            "gender": "male",
                            "date_of_birth": "1995-08-15",
                            "village": "Pune",
                            "district": "Pune",
                            "state": "Maharashtra",
                            "allergies": ["Penicillin"],
                            "chronic_conditions": ["None"],
                            "emergency_contact_name": "Meena Sharma",
                            "emergency_contact_phone": "9111199999",
                            "preferred_language": "hi",
                        })
        assert r.status_code == 200, r.text
        print("✅ Update patient profile OK")

    def test_get_patient_prescriptions(self):
        r = httpx.get(f"{BASE_URL}/api/v1/patients/me/prescriptions",
                      headers=auth(state["patient_token"]),
                      params={"page": 1, "limit": 10, "active_only": False})
        assert r.status_code == 200, r.text
        print("✅ Get patient prescriptions OK")

    def test_get_patient_appointments(self):
        r = httpx.get(f"{BASE_URL}/api/v1/patients/me/appointments",
                      headers=auth(state["patient_token"]),
                      params={"page": 1, "limit": 10})
        assert r.status_code == 200, r.text
        print("✅ Get patient appointments OK")

    def test_get_patient_documents(self):
        r = httpx.get(f"{BASE_URL}/api/v1/patients/me/documents",
                      headers=auth(state["patient_token"]))
        assert r.status_code == 200, r.text
        print("✅ Get patient documents OK")

    def test_upload_patient_document(self):
        r = httpx.post(f"{BASE_URL}/api/v1/patients/me/documents",
                       headers=auth(state["patient_token"]),
                       json={
                           "file_url": "https://storage.example.com/reports/blood_test.pdf",
                           "document_type": "lab_report",
                           "file_name": "blood_test_march2026.pdf",
                           "file_size_kb": 245,
                           "notes": "Annual blood work results",
                       })
        assert r.status_code == 200, r.text
        print("✅ Upload document OK")


# ═════════════════════════════════════════════════════════════════════════════
# DOCTORS — PUBLIC ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

class TestDoctorsPublic:

    def test_list_doctors(self):
        r = httpx.get(f"{BASE_URL}/api/v1/doctors",
                      params={"page": 1, "limit": 10})
        assert r.status_code == 200, r.text
        print("✅ List doctors OK")

    def test_list_doctors_filtered_by_specialization_and_state(self):
        r = httpx.get(f"{BASE_URL}/api/v1/doctors",
                      params={
                          "specialization": "General Physician",
                          "state": "Maharashtra",
                          "page": 1,
                          "limit": 10,
                      })
        assert r.status_code == 200, r.text
        print("✅ List doctors (filtered) OK")


# ═════════════════════════════════════════════════════════════════════════════
# ADMIN
# ═════════════════════════════════════════════════════════════════════════════

class TestAdmin:

    def test_list_pending_doctors(self):
        r = httpx.get(f"{BASE_URL}/api/v1/admin/doctors/pending",
                      headers=auth(state["admin_token"]))
        assert r.status_code == 200, r.text
        doctors = r.json()["data"]
        if doctors:
            state["doctor_profile_id"] = doctors[0]["doctor_profile_id"]
        print(f"✅ Pending doctors — {len(doctors)} found")

    def test_approve_doctor(self):
        if not state["doctor_profile_id"]:
            pytest.skip("No pending doctor profile to approve")
        r = httpx.post(
            f"{BASE_URL}/api/v1/admin/doctors/{state['doctor_profile_id']}/approve",
            headers=auth(state["admin_token"]),
        )
        assert r.status_code == 200, r.text
        print(f"✅ Doctor approved — {state['doctor_profile_id']}")

    def test_list_pending_pharmacies(self):
        r = httpx.get(f"{BASE_URL}/api/v1/admin/pharmacy/pending",
                      headers=auth(state["admin_token"]))
        assert r.status_code == 200, r.text
        pharmacies = r.json()["data"]
        if pharmacies:
            state["pharmacy_profile_id"] = pharmacies[0]["pharmacy_profile_id"]
        print(f"✅ Pending pharmacies — {len(pharmacies)} found")

    def test_approve_pharmacy(self):
        if not state["pharmacy_profile_id"]:
            pytest.skip("No pending pharmacy profile to approve")
        r = httpx.post(
            f"{BASE_URL}/api/v1/admin/pharmacy/{state['pharmacy_profile_id']}/approve",
            headers=auth(state["admin_token"]),
        )
        assert r.status_code == 200, r.text
        print(f"✅ Pharmacy approved — {state['pharmacy_profile_id']}")

    def test_reject_then_reapprove_doctor(self):
        if not state["doctor_profile_id"]:
            pytest.skip("No doctor profile id")
        r = httpx.post(
            f"{BASE_URL}/api/v1/admin/doctors/{state['doctor_profile_id']}/reject",
            headers=auth(state["admin_token"]),
        )
        assert r.status_code == 200, r.text

        r = httpx.post(
            f"{BASE_URL}/api/v1/admin/doctors/{state['doctor_profile_id']}/approve",
            headers=auth(state["admin_token"]),
        )
        assert r.status_code == 200, r.text
        print("✅ Doctor reject + reapprove OK")


# ═════════════════════════════════════════════════════════════════════════════
# DOCTOR — AUTHENTICATED ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

class TestDoctorAuthenticated:

    def test_get_doctor_profile(self):
        r = httpx.get(f"{BASE_URL}/api/v1/doctors/me/profile",
                      headers=auth(state["doctor_token"]))
        assert r.status_code == 200, r.text
        data = r.json().get("data", {})
        # Belt-and-suspenders: ensure doctor_id is populated from profile
        if not state["doctor_id"]:
            state["doctor_id"] = data.get("user_id") or data.get("id")
        print("✅ Get doctor profile OK")

    def test_update_doctor_profile(self):
        r = httpx.patch(f"{BASE_URL}/api/v1/doctors/me/profile",
                        headers=auth(state["doctor_token"]),
                        json={
                            "consultation_fee": 350,
                            "bio": "Passionate about accessible rural healthcare",
                            "hospital_name": "Sunrise Medical Center",
                        })
        assert r.status_code == 200, r.text
        print("✅ Update doctor profile OK")

    def test_toggle_doctor_availability(self):
        r = httpx.patch(f"{BASE_URL}/api/v1/doctors/me/availability",
                        headers=auth(state["doctor_token"]),
                        json={"is_available": True})
        assert r.status_code == 200, r.text
        print("✅ Toggle doctor availability OK")

    def test_get_slot_templates(self):
        r = httpx.get(f"{BASE_URL}/api/v1/doctors/me/slots",
                      headers=auth(state["doctor_token"]))
        assert r.status_code == 200, r.text
        print("✅ Get slot templates OK")

    def test_create_slot_template(self):
        r = httpx.post(f"{BASE_URL}/api/v1/doctors/me/slots",
                       headers=auth(state["doctor_token"]),
                       json={
                           "day_of_week": 5,
                           "start_time": "10:00:00",
                           "end_time": "14:00:00",
                           "slot_duration_min": 30,
                       })
        assert r.status_code == 200, r.text
        print("✅ Create slot template OK")

    def test_get_doctor_appointments(self):
        r = httpx.get(f"{BASE_URL}/api/v1/doctors/me/appointments",
                      headers=auth(state["doctor_token"]),
                      params={"page": 1, "limit": 10})
        assert r.status_code == 200, r.text
        print("✅ Get doctor appointments OK")

    def test_get_doctor_available_slots(self):
        """
        FIX: Use resolve_doctor_id() so this test never sends 'None' as a
        path parameter, which was causing a 422 UUID-parsing error when
        state["doctor_id"] hadn't been populated yet.
        """
        doctor_id = resolve_doctor_id()
        r = httpx.get(
            f"{BASE_URL}/api/v1/doctors/{doctor_id}/slots",
            params={"days": 14},
        )
        assert r.status_code == 200, r.text
        slots = r.json().get("data", [])
        if slots:
            state["_first_slot_time"] = slots[0]["slot_time"]
        print(f"✅ Get available slots OK — {len(slots)} slots found")


# ═════════════════════════════════════════════════════════════════════════════
# APPOINTMENT
# ═════════════════════════════════════════════════════════════════════════════

class TestAppointment:

    def test_book_appointment(self):
        slot_time = state.get("_first_slot_time")
        if not slot_time:
            pytest.skip("No available slot — ensure slot template was created and approved")
        r = httpx.post(f"{BASE_URL}/api/v1/patients/appointments",
                       headers=auth(state["patient_token"]),
                       json={
                           "doctor_id": state["doctor_id"],
                           "slot_time": slot_time,
                           "type": "video",
                           "chief_complaint": "Persistent fever and fatigue for 3 days",
                       })
        assert r.status_code == 200, r.text
        data = r.json().get("data", {})
        state["appointment_id"] = data.get("id") or data.get("appointment_id")
        print(f"✅ Book appointment OK — {state['appointment_id']}")

    def test_doctor_confirm_appointment(self):
        if not state["appointment_id"]:
            pytest.skip("No appointment id — book_appointment must pass first")
        r = httpx.patch(
            f"{BASE_URL}/api/v1/doctors/me/appointments/{state['appointment_id']}",
            headers=auth(state["doctor_token"]),
            json={"status": "confirmed", "notes": "Patient confirmed via phone"},
        )
        assert r.status_code == 200, r.text
        print("✅ Doctor confirmed appointment OK")


# ═════════════════════════════════════════════════════════════════════════════
# PRESCRIPTION
# ═════════════════════════════════════════════════════════════════════════════

class TestPrescription:

    def test_write_prescription(self):
        if not state["patient_profile_id"]:
            pytest.skip("patient_profile_id not set — run TestPatient first")
        r = httpx.post(f"{BASE_URL}/api/v1/doctors/me/prescriptions",
                       headers=auth(state["doctor_token"]),
                       json={
                           "patient_id": state["patient_profile_id"],
                           "diagnosis": "Acute viral fever with myalgia",
                           "medicines": [
                               {
                                   "name": "Paracetamol",
                                   "generic_name": "Acetaminophen",
                                   "dosage": "500mg",
                                   "frequency": "TID",
                                   "duration": "5 days",
                                   "instructions": "Take after food",
                               },
                               {
                                   "name": "Cetirizine",
                                   "dosage": "10mg",
                                   "frequency": "OD",
                                   "duration": "3 days",
                                   "instructions": "Take at bedtime",
                               },
                           ],
                           "advice": "Rest, drink plenty of fluids, avoid cold water",
                           "follow_up_date": "2026-04-15",
                       })
        assert r.status_code == 200, r.text
        print("✅ Write prescription OK")

    def test_get_patient_prescriptions_after_write(self):
        r = httpx.get(f"{BASE_URL}/api/v1/patients/me/prescriptions",
                      headers=auth(state["patient_token"]),
                      params={"page": 1, "limit": 10})
        assert r.status_code == 200, r.text
        data = r.json().get("data", {})
        items = data if isinstance(data, list) else data.get("items", [])
        print(f"✅ Patient prescriptions after write OK — {len(items)} found")


# ═════════════════════════════════════════════════════════════════════════════
# PHARMACY
# ═════════════════════════════════════════════════════════════════════════════

class TestPharmacy:

    def test_search_pharmacies_by_medicine(self):
        r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/search",
                      params={"medicine": "Paracetamol", "in_stock": True})
        assert r.status_code == 200, r.text
        print("✅ Search pharmacies by medicine OK")

    def test_search_pharmacies_with_geolocation(self):
        r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/search",
                      params={
                          "medicine": "Paracetamol",
                          "lat": 17.0575,
                          "lng": 79.2691,
                          "radius_km": 10,
                          "in_stock": True,
                      })
        assert r.status_code == 200, r.text
        print("✅ Search pharmacies with geolocation OK")

    def test_get_pharmacy_profile(self):
        r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/me/profile",
                      headers=auth(state["pharmacy_token"]))
        assert r.status_code == 200, r.text
        print("✅ Get pharmacy profile OK")

    def test_update_pharmacy_profile(self):
        r = httpx.patch(f"{BASE_URL}/api/v1/pharmacy/me/profile",
                        headers=auth(state["pharmacy_token"]),
                        json={
                            "pharmacy_name": "Krishna Medicals & Surgical",
                            "phone": "9111100003",
                            "state": "Telangana",
                            "opening_hours": {
                                "mon": "08:00-21:00",
                                "tue": "08:00-21:00",
                                "sat": "09:00-18:00",
                                "sun": "closed",
                            },
                        })
        assert r.status_code == 200, r.text
        print("✅ Update pharmacy profile OK")

    def test_toggle_pharmacy_open_status(self):
        r = httpx.patch(f"{BASE_URL}/api/v1/pharmacy/me/status",
                        headers=auth(state["pharmacy_token"]),
                        json={"is_open_now": True})
        assert r.status_code == 200, r.text
        print("✅ Toggle pharmacy open status OK")

    def test_add_inventory_item_paracetamol(self):
        r = httpx.post(f"{BASE_URL}/api/v1/pharmacy/me/inventory",
                       headers=auth(state["pharmacy_token"]),
                       json={
                           "medicine_name": "Paracetamol 500mg",
                           "generic_name": "Acetaminophen",
                           "category": "Analgesic",
                           "quantity_in_stock": 500,
                           "price_per_unit": 1.5,
                           "unit": "tablet",
                           "requires_prescription": False,
                       })
        assert r.status_code == 200, r.text
        data = r.json().get("data", {})
        state["inventory_item_id"] = data.get("id") or data.get("item_id")
        print(f"✅ Add inventory item (Paracetamol) OK — {state['inventory_item_id']}")

    def test_add_inventory_item_amoxicillin(self):
        r = httpx.post(f"{BASE_URL}/api/v1/pharmacy/me/inventory",
                       headers=auth(state["pharmacy_token"]),
                       json={
                           "medicine_name": "Amoxicillin 500mg",
                           "generic_name": "Amoxicillin",
                           "category": "Antibiotic",
                           "quantity_in_stock": 200,
                           "price_per_unit": 8.0,
                           "unit": "capsule",
                           "requires_prescription": True,
                       })
        assert r.status_code == 200, r.text
        print("✅ Add inventory item (Amoxicillin) OK")

    def test_get_full_inventory(self):
        r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/me/inventory",
                      headers=auth(state["pharmacy_token"]),
                      params={"page": 1, "limit": 20})
        assert r.status_code == 200, r.text
        print("✅ Get full inventory OK")

    def test_search_inventory(self):
        r = httpx.get(f"{BASE_URL}/api/v1/pharmacy/me/inventory",
                      headers=auth(state["pharmacy_token"]),
                      params={"search": "Paracetamol", "page": 1, "limit": 10})
        assert r.status_code == 200, r.text
        print("✅ Search inventory OK")

    def test_update_inventory_item(self):
        if not state["inventory_item_id"]:
            pytest.skip("inventory_item_id not set — add_inventory must pass first")
        r = httpx.patch(
            f"{BASE_URL}/api/v1/pharmacy/me/inventory/{state['inventory_item_id']}",
            headers=auth(state["pharmacy_token"]),
            json={"quantity_in_stock": 450, "price_per_unit": 1.8},
        )
        assert r.status_code == 200, r.text
        print("✅ Update inventory item OK")


# ═════════════════════════════════════════════════════════════════════════════
# AI
# ═════════════════════════════════════════════════════════════════════════════

class TestAI:

    def test_symptom_check_english(self):
        r = httpx.post(f"{BASE_URL}/api/v1/ai/symptoms",
                       headers=auth(state["patient_token"]),
                       json={
                           "symptoms": "I have had fever of 101F for 2 days, body ache and runny nose",
                           "language": "en",
                       },
                       timeout=30.0)
        assert r.status_code == 200, r.text
        print("✅ AI symptom check (English) OK")

    def test_symptom_check_hindi(self):
        r = httpx.post(f"{BASE_URL}/api/v1/ai/symptoms",
                       headers=auth(state["patient_token"]),
                       json={
                           "symptoms": "Mujhe 2 din se bukhaar hai aur sar dard ho raha hai",
                           "language": "hi",
                       },
                       timeout=30.0)
        # 429 = rate limited; acceptable in CI
        assert r.status_code in [200, 429], r.text
        print("✅ AI symptom check (Hindi) OK — 429 rate-limit is expected in CI")


# ═════════════════════════════════════════════════════════════════════════════
# CONTENT
# ═════════════════════════════════════════════════════════════════════════════

class TestContent:

    def test_daily_tip_hindi(self):
        r = httpx.get(f"{BASE_URL}/api/v1/content/daily-tip",
                      params={"language": "hi", "state": "Maharashtra"})
        assert r.status_code == 200, r.text
        print("✅ Daily tip (Hindi) OK")

    def test_daily_tip_english(self):
        r = httpx.get(f"{BASE_URL}/api/v1/content/daily-tip",
                      params={"language": "en"})
        assert r.status_code == 200, r.text
        print("✅ Daily tip (English) OK")

    def test_first_aid_list(self):
        r = httpx.get(f"{BASE_URL}/api/v1/content/first-aid",
                      params={"language": "hi"})
        assert r.status_code == 200, r.text
        print("✅ First aid list OK")

    def test_first_aid_by_category(self):
        r = httpx.get(f"{BASE_URL}/api/v1/content/first-aid",
                      params={"language": "hi", "category": "burns"})
        assert r.status_code == 200, r.text
        print("✅ First aid by category OK")

    def test_health_facts(self):
        r = httpx.get(f"{BASE_URL}/api/v1/content/health-facts",
                      params={"language": "hi"})
        assert r.status_code == 200, r.text
        print("✅ Health facts OK")

    def test_get_my_notifications(self):
        r = httpx.get(f"{BASE_URL}/api/v1/content/notifications/me",
                      headers=auth(state["patient_token"]),
                      params={"page": 1, "limit": 20})
        assert r.status_code == 200, r.text
        data = r.json().get("data", [])
        if isinstance(data, list) and data:
            state["notification_id"] = data[0].get("id")
        elif isinstance(data, dict):
            items = data.get("items", [])
            if items:
                state["notification_id"] = items[0].get("id")
        print(f"✅ Get notifications OK — id: {state['notification_id']}")

    def test_mark_notification_read(self):
        if not state["notification_id"]:
            pytest.skip("No notification id — notifications list was empty")
        r = httpx.patch(
            f"{BASE_URL}/api/v1/content/notifications/{state['notification_id']}/read",
            headers=auth(state["patient_token"]),
        )
        assert r.status_code == 200, r.text
        print("✅ Mark notification read OK")


# ═════════════════════════════════════════════════════════════════════════════
# AUTH — CLEANUP
# ═════════════════════════════════════════════════════════════════════════════

class TestAuthCleanup:

    def test_logout(self):
        r = httpx.post(f"{BASE_URL}/api/v1/auth/logout",
                       headers=auth(state["patient_token"]))
        assert r.status_code == 200, r.text
        print("✅ Logout OK")