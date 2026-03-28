"""SwasthyaSetu API — FastAPI application entry point."""

import uuid
import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth, patient, doctor, pharmacy, appointments, ai, content
from app.routers import admin


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
    ],
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_headers(request: Request, call_next):
    """Add standard response headers to all responses."""
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Cache"] = "MISS"
    return response


# Routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(patient.router, prefix="/api/v1/patients")
app.include_router(doctor.router, prefix="/api/v1/doctors")
app.include_router(pharmacy.router, prefix="/api/v1/pharmacy")
app.include_router(appointments.router, prefix="/api/v1/appointments")
app.include_router(ai.router, prefix="/api/v1/ai")
app.include_router(content.router, prefix="/api/v1/content")
app.include_router(admin.router, prefix="/api/v1/admin")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        },
    )


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    checks = {"api": "ok"}

    # Check database
    try:
        from app.database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"

    # Check Redis
    try:
        from app.dependencies import get_redis
        redis_client = await get_redis()
        if redis_client:
            await redis_client.ping()
            checks["redis"] = "ok"
        else:
            checks["redis"] = "unavailable"
    except Exception:
        checks["redis"] = "unavailable"

    overall = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}
