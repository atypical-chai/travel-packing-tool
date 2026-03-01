"""
Pydantic models for request/response shapes.
FastAPI uses these to validate incoming JSON and document the API.
"""
from pydantic import BaseModel
from typing import List


class TripDetailsRequest(BaseModel):
    """What the frontend sends when generating a checklist."""
    destination: str
    tripType: str
    travellingWith: List[str]
    season: str


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
    travelers: List[str]
    seasons: List[str]
