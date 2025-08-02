from fastapi import APIRouter
from pydantic import BaseModel
from utils.gemini_client import suggest_tourist_places

router = APIRouter()

class LocationRequest(BaseModel):
    address: str

@router.post("/api/suggest")
async def suggest_places(req: LocationRequest):
    print("Received address:", req.address)
    places = suggest_tourist_places(req.address)
    print("Places returned:", places)
    return {"places": places}
