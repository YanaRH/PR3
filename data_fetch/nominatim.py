import requests
from typing import List, Dict, Optional
from config.settings import NOMINATIM_USER_AGENT, COUNTRIES

def get_country_location(country_name: str) -> Optional[Dict]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": country_name,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    headers = {"User-Agent": NOMINATIM_USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    place = data[0]
    return {
        "name": country_name,
        "latitude": float(place["lat"]),
        "longitude": float(place["lon"]),
    }

def fetch_countries() -> List[Dict]:
    results = []
    for c in COUNTRIES:
        loc = get_country_location(c)
        if loc:
            results.append(loc)
    # Если нужно ровно 10, можно добавить ещё стран в COUNTRIES в settings.py
    return results
