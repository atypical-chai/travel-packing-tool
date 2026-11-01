"""
FastAPI app: API server for the Travel Packing List.
Endpoints: GET /, GET /api/form-options, POST /api/generate-checklist.

On AWS Lambda, Mangum adapts API Gateway events to ASGI (handler below).
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import TripDetailsRequest, ChecklistData, FormOptionsResponse
from list_generator import generate_checklist

app = FastAPI(title="Travel Packing List API")

# Exact origins only. Override with comma-separated CORS_ORIGINS for AWS staging.
_DEFAULT_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://travel-packing-tool.vercel.app",
    # AWS staging CloudFront (pilot). Exact origin; keep Vercel for rollback.
    "https://d1ygtemkaj8b77.cloudfront.net",
    "null",
]


def _cors_origins():
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if not raw:
        return list(_DEFAULT_ORIGINS)
    origins = [part.strip() for part in raw.split(",") if part.strip()]
    # Keep local + Vercel during the dual-host pilot so rollbacks stay usable.
    for origin in _DEFAULT_ORIGINS:
        if origin not in origins:
            origins.append(origin)
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Welcome message and pointer to docs."""
    return {
        "message": "Travel Packing List API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/form-options", response_model=FormOptionsResponse)
def get_form_options():
    """Return dropdown/checkbox options for the trip form."""
    return FormOptionsResponse(
        tripTypes=["general", "work", "outdoor"],
        weather=["hot", "cold", "rain", "pleasant"],
        gear=["laptop", "camera"],
        activities=["beach", "fitness", "roadtrip", "downtime"],
        tripScope=["domestic", "international"],
    )


@app.post("/api/generate-checklist", response_model=ChecklistData)
def post_generate_checklist(body: TripDetailsRequest):
    """Generate personalized packing list from trip details."""
    result = generate_checklist(
        trip_type=body.tripType,
        weather=body.weather or [],
        gear=body.gear or [],
        activities=body.activities or [],
        trip_scope=body.tripScope or "domestic",
    )
    return ChecklistData(**result)


# AWS Lambda entrypoint (unused on Render / local uvicorn).
try:
    from mangum import Mangum

    handler = Mangum(app, lifespan="off")
except ImportError:  # pragma: no cover - Render/local without mangum installed
    handler = None


if __name__ == "__main__":
    """Run with: python main.py (reads PORT from env for Render)."""
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
