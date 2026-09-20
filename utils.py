from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    """Расчёт расстояния между двумя точками на Земле (формула гаверсинуса)."""
    R = 6371  # радиус Земли в км
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def filter_aircraft_by_country(aircraft_data, country_coords, radius=500):
    """
    Фильтрует самолёты по воздушному пространству страны.
    Использует расчёт расстояния от центра страны.
    """
    filtered = []
    for aircraft in aircraft_data:
        lat = aircraft.get("latitude")
        lon = aircraft.get("longitude")
        if lat is None or lon is None:
            continue
        distance = calculate_distance(
            country_coords["lat"], country_coords["lon"], lat, lon
        )
        if distance <= radius:
            filtered.append(aircraft)
    return filtered


def handle_rate_limit(delay=2):
    """Пауза между запросами для соблюдения rate-limit API."""
    import time
    time.sleep(delay)


