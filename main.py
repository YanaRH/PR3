import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

try:
    from db_manager import DBManager
    from data_fetch.countries import fetch_countries_data
    from api_client import get_aircrafts_data
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)


def main():
    try:
        db = DBManager()

        # Страны
        print("\n🌍 Получение данных о странах...")
        countries_data = fetch_countries_data()
        if countries_data:
            db.save_countries(countries_data)

        # Самолёты
        print("\n✈️ Получение данных о воздушных судах...")
        aircrafts_data = get_aircrafts_data()
        if aircrafts_data:
            db.save_aircrafts(aircrafts_data)

        print("\n🚀 Данные успешно сохранены в БД!")

    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


if __name__ == "__main__":
    main()


