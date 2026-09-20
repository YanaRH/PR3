import requests

from config.settings import NOMINATIM_URL, HEADERS

OPENSKY_STATES_URL = "https://opensky-network.org/api/states/all"


def get_country_coordinates(country_name: str):
    """
    Получает координаты страны через Nominatim API.
    Возвращает словарь {"lat": float, "lon": float} или None.
    """
    params = {"country": country_name, "format": "json", "limit": 1}
    try:
        response = requests.get(
            NOMINATIM_URL, headers=HEADERS, params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
    except Exception as e:
        print(f"⚠️ Ошибка получения координат для {country_name}: {e}")
        return None


def get_aircrafts_data():
    """
    Получает данные о воздушных судах через OpenSky Network API.
    Возвращает список словарей с распарсенными полями.
    """
    try:
        response = requests.get(OPENSKY_STATES_URL, timeout=15)
        response.raise_for_status()
        states = response.json().get("states", [])

        aircrafts = []
        for state in states:
            try:
                aircrafts.append({
                    "icao24": state[0],
                    "callsign": state[1],
                    "origin_country": state[2],
                    "time_position": state[3],
                    "longitude": state[5],
                    "latitude": state[6],
                    "baro_altitude": state[7],
                    "velocity": state[9],
                    "heading": state[10],
                    "vertical_rate": state[11],
                    "last_contact": state[4],
                    "on_ground": state[8] == 1,
                })
            except IndexError:
                continue
        return aircrafts
    except Exception as e:
        print(f"⚠️ Ошибка получения данных о самолётах: {e}")
        return []
