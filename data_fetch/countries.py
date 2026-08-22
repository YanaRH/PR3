import os
import requests
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

COUNTRIES_LIST = [
    "Russia", "United States", "China", "India", "Brazil",
    "Australia", "Canada", "Germany", "France", "Japan",
    "United Kingdom", "Italy", "Spain", "South Africa", "Argentina"
]

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Получаем email из .env — без хардкода
NOMINATIM_EMAIL = os.getenv("NOMINATIM_EMAIL")
if not NOMINATIM_EMAIL:
    raise ValueError("Не задана переменная окружения NOMINATIM_EMAIL в файле .env")

HEADERS = {
    "User-Agent": f"AircraftDataProject ({NOMINATIM_EMAIL})"
}

# Конфигурация БД из переменных окружения
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "aircraft_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}


def create_tables(cursor):
    """Создаёт таблицы countries и aircrafts, если их нет."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            radius_km DOUBLE PRECISION DEFAULT 800.0
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aircrafts (
            id SERIAL PRIMARY KEY,
            icao24 VARCHAR(8),
            callsign VARCHAR(20),
            origin_country VARCHAR(100),
            time_position TIMESTAMP,
            last_position_time TIMESTAMP,
            longitude DOUBLE PRECISION,
            latitude DOUBLE PRECISION,
            baro_altitude DOUBLE PRECISION,
            velocity DOUBLE PRECISION,
            true_track DOUBLE PRECISION,
            vertical_rate DOUBLE PRECISION,
            geo_altitude DOUBLE PRECISION,
            squawk VARCHAR(4),
            spi BOOLEAN
        );
    """)
    print("✅ Таблицы проверены/созданы.")


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
    except Exception as e:
        print(f"⚠️ Ошибка получения координат для {country_name}: {e}")
        return None


def save_countries_to_db() -> int:
    """Загружает или обновляет данные о странах в таблице countries."""
    conn = None
    cursor = None
    saved_count = 0

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Автосоздание таблиц при каждом запуске
        create_tables(cursor)

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
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return saved_count
