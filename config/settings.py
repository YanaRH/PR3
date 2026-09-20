import os

# --- Настройки базы данных ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "air_project")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("Не все переменные окружения загружены из .env!")

# Единый словарь для psycopg2
DB_CONFIG = {
    "host": DB_HOST,
    "port": int(DB_PORT),
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
}

# --- Список стран ---
COUNTRIES = [
    "Russia", "United States", "China", "India", "Brazil",
    "Australia", "Canada", "Germany", "France", "Japan",
    "United Kingdom", "Italy", "Spain", "South Africa", "Argentina",
]

# --- Настройки Nominatim ---
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_EMAIL = os.getenv("NOMINATIM_EMAIL")
if not NOMINATIM_EMAIL:
    raise ValueError("Не задана переменная NOMINATIM_EMAIL в .env")

HEADERS = {
    "User-Agent": f"AircraftDataProject ({NOMINATIM_EMAIL})"
}

