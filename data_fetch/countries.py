import requests

from config.settings import COUNTRIES, NOMINATIM_URL, HEADERS
from api_client import get_country_coordinates


def fetch_countries_data():
    """
    Получает координаты для всех стран из COUNTRIES.
    Возвращает список словарей: {"name": str, "lat": float, "lon": float}
    """
    results = []
    for country in COUNTRIES:
        coords = get_country_coordinates(country)
        if coords:
            results.append({
                "name": country,
                "lat": coords["lat"],
                "lon": coords["lon"],
            })
            print(f"  ✔️ {country}")
        else:
            print(f"  ⚠️ {country} — координаты не получены")
    return results
