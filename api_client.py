import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_EMAIL = os.getenv("API_EMAIL")


def get_country_coordinates(country_name):
    """
    Получает координаты страны через Nominatim.
    ИСПРАВЛЕНО: в заголовках нет заглушки (your_email@example.com).
    """
    url = "https://nominatim.openstreetmap.org/search"

    # ВАЖНО: используем реальный email из .env
    headers = {
        "User-Agent": f"AirProject/1.0 ({API_EMAIL})"
    }

    params = {
        "q": country_name,
        "format": "json",
        "limit": 1
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if data:
        return data[0]["lat"], data[0]["lon"]
    return None, None


def get_aircrafts_data():
    """
    Получает данные о самолетах через OpenSky Network API.
    Возвращает список словарей.
    """
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)
    response.raise_for_status()
    states = response.json()["states"]

    aircrafts = []
    for state in states:
        # state: [icao24, callsign, origin_country, time_position, lon, lat, baro_altitude, ...]
        aircrafts.append({
            "icao24": state[0],
            "callsign": state[1],
            "origin_country": state[2],
            "time_position": state[3],  # int (Unix timestamp) — подходит для BIGINT
            "longitude": state[4],
            "latitude": state[5],
            "baro_altitude": state[6],
            "velocity": state[9],  # velocity
            "heading": state[10],
            "vertical_rate": state[11],
            "last_contact": state[8]  # last_contact
        })
    return aircrafts
