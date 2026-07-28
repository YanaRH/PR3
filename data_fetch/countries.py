import requests
import psycopg2

COUNTRIES_LIST = [
    "Russia", "United States", "China", "India", "Brazil",
    "Australia", "Canada", "Germany", "France", "Japan",
    "United Kingdom", "Italy", "Spain", "South Africa", "Argentina"
]

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "AircraftDataProject/1.0 (your_email@example.com)"}


def get_country_coordinates(country_name: str):
    """Получает координаты (широта, долгота) для указанной страны через Nominatim API."""
    params = {"country": country_name, "format": "json", "limit": 1}
    try:
        response = requests.get(NOMINATIM_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
    except Exception:
        return None


def save_countries_to_db(db_config: dict) -> int:
    """Загружает или обновляет данные о странах в таблице countries."""
    conn = None
    cursor = None
    saved_count = 0
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM countries;")
        count = cursor.fetchone()[0]
        if count >= 10:
            print(f"✅ В таблице уже есть {count} стран. Пропускаем загрузку.")
            return count

        print(f"📥 Загружаем координаты для {len(COUNTRIES_LIST)} стран...")
        for country in COUNTRIES_LIST:
            coords = get_country_coordinates(country)
            if coords:
                query = """
                    INSERT INTO countries (name, latitude, longitude, radius_km)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        radius_km = EXCLUDED.radius_km;
                """
                cursor.execute(query, (country, coords["lat"], coords["lon"], 800.0))
                saved_count += 1
                print(f"  ✔️ {country}")

        conn.commit()
        print(f"🎉 Сохранено: {saved_count} записей.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"❌ Ошибка БД при загрузке стран: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return saved_count
