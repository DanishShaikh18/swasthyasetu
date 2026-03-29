# SwasthyaSetu — स्वास्थ्य सेतु (Health Bridge)

**Production-grade rural telemedicine platform for India** — connecting patients in remote areas with qualified doctors through AI-powered symptom checking, video consultations, multilingual support, and nearby pharmacy search.

---

## 🚀 Live Demo

**Backend API:** https://swasthyasetu-production.up.railway.app/docs

### Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Doctor | rajesh.sharma@ss.dev | doctor123 |
| Doctor | priya.deshmukh@ss.dev | doctor123 |
| Patient | ramesh.p@ss.dev | patient123 |
| Patient | priyanka.p@ss.dev | patient123 |
| Pharmacy | sharma.meds@ss.dev | pharmacy123 |
| Pharmacy | deshmukh.pharma@ss.dev | pharmacy123 |

---

## Architecture
```
swasthyasetu/
├── backend/              # FastAPI (Python 3.11+)
│   ├── app/
│   │   ├── main.py       # Entry point
│   │   ├── config.py     # Pydantic Settings
│   │   ├── database.py   # Async SQLAlchemy
│   │   ├── dependencies.py # Auth, rate limiting, Redis
│   │   ├── models/       # 13 SQLAlchemy models
│   │   ├── schemas/      # 6 Pydantic schema files
│   │   ├── routers/      # 8 API routers (44 endpoints)
│   │   └── services/     # 5 services (auth, AI, video, notification, storage)
│   ├── alembic/          # Database migrations
│   ├── seed/             # 4 seed data scripts
│   ├── Dockerfile
│   └── requirements.txt
├── patient-app/          # React + Vite + PWA (port 5173)
│   └── src/              # 10 pages, 6 components, 10 languages
├── doctor-portal/        # React + Vite (port 5174)
│   └── src/              # 7 pages with sidebar layout
├── pharmacy-portal/      # React + Vite (port 5175)
│   └── src/              # 5 pages with inventory management
└── docker-compose.yml    # PostGIS + Redis + Backend
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| Database | PostgreSQL 15 + PostGIS (geospatial) via Supabase |
| Cache | Redis 7 via Railway |
| Auth | JWT (access + refresh tokens), bcrypt |
| AI | Google Gemini Flash API |
| Video | Daily.co |
| Notifications | Firebase Cloud Messaging |
| Storage | Supabase Storage |
| Frontend | React 18, Vite, Tailwind CSS v4, Zustand |
| i18n | 10 Indian languages (hi, en, ta, te, mr, gu, kn, ml, pa, or) |
| Offline | PWA + IndexedDB + Service Worker |
| Hosting | Railway (backend + Redis), Supabase (PostgreSQL + PostGIS) |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 1. Clone & Configure
```bash
cd swasthyasetu
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys (optional — features degrade gracefully)
```

### 2. Start Backend (Docker)
```bash
docker-compose up -d
# This starts PostgreSQL + PostGIS, Redis, and the FastAPI backend
# Seeds are run automatically on first start
# API docs: http://localhost:8000/docs
```

### 3. Start Frontends
```bash
# Patient App (port 5173)
cd patient-app && npm install && npm run dev

# Doctor Portal (port 5174)
cd doctor-portal && npm install && npm run dev

# Pharmacy Portal (port 5175)
cd pharmacy-portal && npm install && npm run dev
```

### Without Docker (manual)
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m seed.seed_content
python -m seed.seed_doctors
python -m seed.seed_pharmacies
python -m seed.seed_patients
uvicorn app.main:app --reload
```

---

## API Endpoints (44 total)

### Auth (`/api/v1/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | /register | Register (patient/doctor/pharmacy) |
| POST | /login | Login (returns JWT) |
| POST | /refresh | Refresh access token |
| POST | /logout | Logout (blocklist token) |

### Patient (`/api/v1/patients`)
| Method | Path | Description |
|--------|------|-------------|
| GET | /me | Get profile |
| PATCH | /me | Update profile |
| GET | /me/prescriptions | Paginated prescriptions |
| GET | /me/appointments | Paginated appointments |
| POST | /appointments | Book appointment |
| GET | /me/documents | List documents |
| POST | /me/documents | Upload document |

### Doctor (`/api/v1/doctors`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | Public doctor listing (filterable) |
| GET | /{doctor_id}/slots | Available slots for next N days |
| GET | /me/profile | Doctor profile |
| PATCH | /me/profile | Update profile |
| PATCH | /me/availability | Toggle online/offline |
| GET | /me/appointments | Appointments (filterable by status) |
| PATCH | /me/appointments/{appointment_id} | Accept/reject/complete |
| GET | /me/patients/{patient_id} | View patient record (audit logged) |
| POST | /me/prescriptions | Write prescription (dual-write) |
| GET | /me/slots | Slot templates |
| POST | /me/slots | Create slot template, auto-generates bookable slots |

### Pharmacy (`/api/v1/pharmacy`)
| Method | Path | Description |
|--------|------|-------------|
| GET | /search | PostGIS geospatial medicine search |
| GET | /me/profile | Pharmacy profile |
| PATCH | /me/profile | Update profile |
| PATCH | /me/status | Toggle open/closed |
| GET | /me/inventory | Search inventory |
| POST | /me/inventory | Add medicine |
| PATCH | /me/inventory/{item_id} | Update medicine |
| POST | /me/inventory/bulk | CSV bulk upload |

### Appointments (`/api/v1/appointments`)
| Method | Path | Description |
|--------|------|-------------|
| GET | /{appointment_id}/join | Generate video call token (never stored) |

### AI (`/api/v1/ai`)
| Method | Path | Description |
|--------|------|-------------|
| POST | /symptoms | AI symptom checker (rate limited 5/user/hour) |

### Content (`/api/v1/content`)
| Method | Path | Description |
|--------|------|-------------|
| GET | /daily-tip | Daily health tip (cached 24h) |
| GET | /first-aid | First aid cards (cached 7d) |
| GET | /health-facts | Health facts (cached 6h) |
| GET | /notifications/me | User notifications |
| PATCH | /notifications/{notification_id}/read | Mark notification read |

### Admin (`/api/v1/admin`)
| Method | Path | Description |
|--------|------|-------------|
| GET | /doctors/pending | List pending doctor approvals |
| POST | /doctors/{doctor_profile_id}/approve | Approve doctor |
| POST | /doctors/{doctor_profile_id}/reject | Reject doctor |
| GET | /pharmacy/pending | List pending pharmacy approvals |
| POST | /pharmacy/{pharmacy_profile_id}/approve | Approve pharmacy |
| POST | /pharmacy/{pharmacy_profile_id}/reject | Reject pharmacy |

### General
| Method | Path | Description |
|--------|------|-------------|
| GET | / | API info |
| GET | /health | Health check (DB + Redis status) |

---

## Seed Data

| Data | Count | Details |
|------|-------|---------|
| Doctors | 20 | 8 specializations across 10 Indian states |
| Pharmacies | 15 | Real GPS coordinates, 40+ medicines each |
| Patients | 10 | With appointments and prescriptions |
| Health Content | 38 | First aid, daily tips, nutrition, seasonal alerts (Hindi + English) |

---

## External API Keys (Optional)

All external services degrade gracefully when keys are missing:

| Service | Env Variable | Fallback |
|---------|-------------|----------|
| Gemini AI | `GEMINI_API_KEY` | Returns general health advice |
| Daily.co | `DAILY_API_KEY` | Mock video tokens |
| Supabase | `SUPABASE_URL` + `SUPABASE_KEY` | Mock upload URLs |
| Firebase | `FIREBASE_CREDENTIALS_JSON` | Notifications logged only |

---

## Design Decisions

- **Security**: JWT with 15-min access tokens, Redis-stored refresh tokens (7-day TTL), bcrypt (12 rounds), role-based access
- **Dual-write prescriptions**: Both JSONB (for display) and flat `prescription_items` table (for search/analytics)
- **Audit logging**: Sensitive actions (viewing patient records, writing prescriptions) logged asynchronously
- **Video tokens**: Generated on-demand, NEVER stored in database
- **Rate limiting**: AI symptom checks limited to 5/user/hour via Redis
- **Graceful degradation**: Every external service has a fallback — app works without any API keys
- **PostGIS**: Real geospatial pharmacy search within configurable radius
- **10 Indian languages**: Full translations for Hindi/English, core translations for 8 more
- **PWA**: Patient app works offline with IndexedDB caching

---

## License

MIT