import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
if not OPENCAGE_API_KEY:
    raise ValueError("OPENCAGE_API_KEY missing")

def get_coordinates_from_address(address):
    url = (
        "https://api.opencagedata.com/geocode/v1/json"
        f"?q={requests.utils.quote(address)}&key={OPENCAGE_API_KEY}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data["status"]["code"] != 200 or not data["results"]:
        raise Exception("Invalid geocode response")
    geom = data["results"][0]["geometry"]
    return geom["lat"], geom["lng"]

def fetch_nearby_wikipedia(lat, lng, radius=20000, limit=8):
    try:
        q = {
            "action": "query",
            "list": "geosearch",
            "gsradius": radius,
            "gscoord": f"{lat}|{lng}",
            "gslimit": limit,
            "format": "json"
        }
        resp = requests.get("https://en.wikipedia.org/w/api.php", params=q, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("query", {}).get("geosearch", [])
        places = []
        for p in data:
            pid = p["pageid"]
            t = p["title"]
            lt, ln = p["lat"], p["lon"]
            img_q = {"action": "query", "pageids": pid, "prop": "pageimages",
                     "pithumbsize": 400, "format": "json"}
            ir = requests.get("https://en.wikipedia.org/w/api.php", params=img_q, timeout=10)
            thumb = ir.json().get("query", {}).get("pages", {}).get(str(pid), {}).get("thumbnail", {}).get("source", "")
            places.append({
                "name": t,
                "address": "",
                "latitude": lt,
                "longitude": ln,
                "image": thumb,
                "wiki": f"https://en.wikipedia.org/?curid={pid}"
            })
        return places
    except Exception as e:
        print("Wikipedia error:", e)
        return []
