# travel-companion-backend/utils/geocode_utils.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

def get_coordinates_from_address(address: str):
    """
    Fetches latitude and longitude for a given address using OpenCage Geocoding API.
    """
    if not OPENCAGE_API_KEY:
        print("Error: OPENCAGE_API_KEY not found in environment variables.")
        return None

    url = f"https://api.opencagedata.com/geocode/v1/json?q={requests.utils.quote(address)}&key={OPENCAGE_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()

        if data["results"]:
            geometry = data["results"][0]["geometry"]
            return {"lat": geometry["lat"], "lng": geometry["lng"]}
        print(f"No coordinates found by OpenCage for address: {address}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates for '{address}' from OpenCage: {e}")
        return None