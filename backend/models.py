"""
Pydantic models for request/response shapes.
FastAPI uses these to validate incoming JSON and document the API.
"""
from pydantic import BaseModel
from typing import List


class TripDetailsRequest(BaseModel):
    """What the frontend sends when generating a checklist."""
    destination: str
    tripType: str  # general | work | outdoor | roadtrip
    weather: List[str]  # hot, cold, rain (checkboxes)
    gear: List[str]  # laptop, camera (checkboxes)
    activities: List[str]  # beach, fitness (checkboxes)
    tripScope: str  # domestic | international


class ChecklistItem(BaseModel):
    """One item in pack, buy, or do list."""
    text: str
    completed: bool


class ChecklistData(BaseModel):
    """Response: the three lists for the packing checklist."""
    pack: List[ChecklistItem]
    buy: List[ChecklistItem]
    do: List[ChecklistItem]


class FormOptionsResponse(BaseModel):
    """Response: dropdown/checkbox options for the trip form."""
    tripTypes: List[str]
    weather: List[str]
    gear: List[str]
    activities: List[str]
    tripScope: List[str]
