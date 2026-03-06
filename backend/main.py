"""
FastAPI app: API server for the Travel Packing List.
Endpoints: GET /, GET /api/form-options, POST /api/generate-checklist.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import TripDetailsRequest, ChecklistData, FormOptionsResponse
from list_generator import generate_checklist

app = FastAPI(title="Travel Packing List API")

# Allow frontend (e.g. Live Server on port 5500) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "null"],
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
        tripTypes=["trek", "leisure", "work", "backpacking"],
        travelers=["me", "parents", "partner", "kids", "friends"],
        seasons=["summer", "winter", "autumn", "spring"],
    )


@app.post("/api/generate-checklist", response_model=ChecklistData)
def post_generate_checklist(body: TripDetailsRequest):
    """Generate personalized packing list from trip details."""
    result = generate_checklist(
        trip_type=body.tripType,
        travelling_with=body.travellingWith,
        season=body.season,
    )
    return ChecklistData(**result)


if __name__ == "__main__":
    """Run with: python main.py (reads PORT from env for Render)."""
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
