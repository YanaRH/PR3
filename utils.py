import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

# Заголовки для API запросов
HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'MonitoringApp/1.0',
    'Authorization': f'Bearer {os.getenv("OPENSKY_API_KEY")}'
}

# Базовые URL для API
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
OPENSKY_STATES_URL = 'https://opensky-network.org/api/states/all'


def get_country_coordinates(country_name):
    """
    Получает координаты страны по её названию
    """
    try:
        params = {
            'q': country_name,
            'format': 'json',
            'limit': 1
        }
        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers={'User-Agent': 'MonitoringApp/1.0'}
        )

        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    'name': country_name,
                    'coordinates': {
                        'lat': data[0].get('lat'),
                        'lon': data[0].get('lon')
                    }
                }
        return None
    except Exception as e:
        print(f"Ошибка при получении координат страны: {str(e)}")
        return None


def get_aircraft_states():
    """
    Получает текущее состояние всех воздушных судов
    """
    try:
        response = requests.get(
            OPENSKY_STATES_URL,
            headers=HEADERS
        )

        if response.status_code == 200:
            return response.json().get('states', [])
        return []
    except Exception as e:
        print(f"Ошибка при получении данных о самолетах: {str(e)}")
        return []


def parse_aircraft_data(states):
    """
    Парсит сырые данные о самолетах в удобный формат
    """
    parsed_data = []

    for state in states:
        try:
            parsed_data.append({
                'registration': state[0],
                'callsign': state[1],
                'x': state[5],  # широта
                'y': state[6],  # долгота
                'altitude': state[7],
                'velocity': state[8],
                'heading': state[9],
                'vertical_rate': state[10],
                'on_ground': state[12] == 1,
                'time_position': int(time.time())  # текущее время в timestamp
            })
        except IndexError:
            continue

    return parsed_data


def filter_aircraft_by_country(aircraft_data, country_coords):
    """
    Фильтрует самолеты по воздушному пространству страны
    """
    # Простая фильтрация по координатам (нужна более точная реализация)
    filtered = []
    for aircraft in aircraft_data:
        if (country_coords['lat'] - 1 <= aircraft['x'] <= country_coords['lat'] + 1 and
                country_coords['lon'] - 1 <= aircraft['y'] <= country_coords['lon'] + 1):
            filtered.append(aircraft)
    return filtered


def get_selected_countries():
    """
    Возвращает список выбранных стран для мониторинга
    """
    return [
        'Россия',
        'США',
        'Китай',
        'Германия',
        'Франция'
    ]


def fetch_and_process_data():
    """
    Основная функция для получения и обработки данных
    """
    countries = get_selected_countries()
    all_aircraft = get_aircraft_states()
    parsed_aircraft = parse_aircraft_data(all_aircraft)

    for country in countries:
        coords = get_country_coordinates(country)
        if coords:
            filtered_aircraft = filter_aircraft_by_country(parsed_aircraft, coords)
            # Здесь можно сохранить данные в БД
            print(f"Самолеты в воздушном пространстве {country}:")
            for ac in filtered_aircraft:
                print(f"Позывной: {ac['callsign']}, Скорость: {ac['velocity']} км/ч")
            print("-" * 40)


def get_selected_countries():
    """
    Возвращает список выбранных стран для мониторинга
    """
    return [
        'Россия',
        'США',
        'Китай',
        'Германия',
        'Франция'
    ]


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Расчет расстояния между двумя точками на Земле
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # радиус Земли в км
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def filter_aircraft_by_country_advanced(aircraft_data, country_coords, radius=500):
    """
    Улучшенная фильтрация самолетов по воздушному пространству страны
    """
    filtered = []
    for aircraft in aircraft_data:
        distance = calculate_distance(
            country_coords['lat'],
            country_coords['lon'],
            aircraft['x'],
            aircraft['y']
        )
        if distance <= radius:
            filtered.append(aircraft)
    return filtered


def handle_rate_limit():
    """
    Обработка ограничения по частоте запросов
    """
    time.sleep(2)  # пауза между запросами


def main():
    try:
        print("Запуск мониторинга воздушных судов...")
        handle_rate_limit()
        fetch_and_process_data()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    main()

