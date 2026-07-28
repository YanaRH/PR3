import os
import time
from typing import Dict, Any

# Импорты из модулей
from db_manager import DBManager
from data_fetch.countries import save_countries_to_db
from data_fetch.opensky import fetch_aircraft_data


def get_db_config() -> Dict[str, Any]:
    """Возвращает конфигурацию для подключения к PostgreSQL."""
    return {
        "dbname": "aircraft_db",
        "user": "postgres",
        "password": "5432",
        "host": "localhost",
        "port": 5432
    }


def main():
    print("🚀 Запуск проекта Aircraft Data Monitor...")
    db_config = get_db_config()

    if db_config["password"] == "ТВОЙ_ПАРОЛЬ_POSTGRES":
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Вставь свой пароль от PostgreSQL в коде!")
        return

    print("\n🌍 Загрузка данных о странах (Nominatim)...")
    save_countries_to_db(db_config)

    print("\n✈️ Загрузка данных о самолетах (OpenSky)...")
    count = fetch_aircraft_data(db_config)
    print(f"✅ Успешно сохранено: {count} записей о самолетах.")

    time.sleep(2)

    print("\n📊 Демонстрация методов класса DBManager:")
    db = DBManager(**db_config)

    try:
        # 1. JOIN: Страны и количество самолетов
        print("\n--- 1. Список стран и количество самолетов (JOIN) ---")
        stats = db.get_countries_and_aeroplanes_count()
        for row in stats:
            print(f"  🗺️ {row['name']}: {row['total_aircrafts']} самолетов")

        # 2. Все самолеты
        print("\n--- 2. Все воздушные суда (первые 5) ---")
        all_planes = db.get_all_aeroplanes()
        for plane in all_planes[:5]:
            print(f"  🛫 {plane['callsign']} | Координаты: {plane['latitude']}, {plane['longitude']}")
        if len(all_planes) > 5:
            print(f"  ... и еще {len(all_planes) - 5} записей.")

        # 3. Средняя скорость
        print("\n--- 3. Средняя скорость всех самолетов ---")
        avg_speed = db.get_avg_speed()
        print(f"  📈 Средняя скорость: {avg_speed:.2f} м/с")

        # 4. Самолеты быстрее среднего
        print("\n--- 4. Самолеты со скоростью выше средней ---")
        fast_planes = db.get_aeroplanes_with_higher_speed()
        print(f"  ⚡ Найдено быстрых самолетов: {len(fast_planes)}")
        for plane in fast_planes[:5]:
            print(f"  🏁 {plane['callsign']} | Скорость: {plane['velocity']} м/с")

        # 5. Поиск по ключевому слову
        print("\n--- 5. Поиск самолетов по ключевому слову 'SU' ---")
        search_result = db.get_aeroplanes_with_keyword("SU")
        print(f"  🔍 Найдено совпадений: {len(search_result)}")
        for plane in search_result[:5]:
            print(f"  🔎 {plane['callsign']} ({plane['icao24']})")

    except Exception as e:
        print(f"❌ Ошибка при выполнении запросов к БД: {e}")
    finally:
        db.close()
        print("\n🏁 Работа программы завершена.")


if __name__ == "__main__":
    main()

