import os

# Получаем данные из .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Формируем строку подключения динамически
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("Ошибка конфигурации: не все переменные окружения загружены из .env!")

DB_DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

COUNTRIES = [
    "Russia", "Germany", "France", "Italy", "Spain",
    "Poland", "Turkey", "India", "Brazil", "Japan"
]

NOMINATIM_USER_AGENT = "aircraft_tracker_project"

