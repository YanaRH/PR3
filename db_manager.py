import psycopg2
from datetime import datetime

from config.settings import DB_CONFIG


class DBManager:
    """Менеджер базы данных. Работает через psycopg2, без ORM."""

    def __init__(self):
        """Инициализация соединения и создание таблиц."""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ Подключение к БД установлено.")
            self._ensure_tables()
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise

    def _ensure_tables(self):
        """Создаёт таблицы, если они ещё не существуют."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                radius_km DOUBLE PRECISION DEFAULT 800.0
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS aircrafts (
                id SERIAL PRIMARY KEY,
                icao24 VARCHAR(8),
                callsign VARCHAR(20),
                origin_country VARCHAR(100),
                time_position TIMESTAMP,
                last_contact TIMESTAMP,
                longitude DOUBLE PRECISION,
                latitude DOUBLE PRECISION,
                baro_altitude DOUBLE PRECISION,
                velocity DOUBLE PRECISION,
                heading DOUBLE PRECISION,
                vertical_rate DOUBLE PRECISION,
                on_ground BOOLEAN
            );
        """)
        self.conn.commit()
        print("✅ Таблицы проверены/созданы.")

    @staticmethod
    def _convert_timestamp(raw_time):
        """Конвертация Unix-времени в datetime. Обрабатывает секунды и миллисекунды."""
        if raw_time is None:
            return None
        if isinstance(raw_time, datetime):
            return raw_time
        if isinstance(raw_time, (int, float)):
            if raw_time > 2147483647:
                return datetime.fromtimestamp(raw_time / 1000.0)
            return datetime.fromtimestamp(raw_time)
        return None

    # --- Методы записи ---

    def save_countries(self, countries_data):
        """
        Сохраняет данные о странах.
        countries_data — список словарей: {"name": str, "lat": float, "lon": float}
        """
        for country in countries_data:
            query = """
                INSERT INTO countries (name, latitude, longitude, radius_km)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    radius_km = EXCLUDED.radius_km;
            """
            try:
                self.cursor.execute(query, (
                    country["name"],
                    country["lat"],
                    country["lon"],
                    800.0,
                ))
            except Exception as e:
                print(f"Ошибка при добавлении страны {country['name']}: {e}")
                self.conn.rollback()
        self.conn.commit()
        print(f"✅ Сохранено стран: {len(countries_data)}")

    def save_aircrafts(self, aircrafts_data):
        """
        Массовая вставка данных о самолётах.
        aircrafts_data — список словарей из api_client.get_aircrafts_data().
        """
        if not aircrafts_data:
            print("⚠️ Нет данных для вставки в таблицу aircrafts.")
            return

        query = """
            INSERT INTO aircrafts (
                icao24, callsign, origin_country, time_position,
                last_contact, longitude, latitude, baro_altitude,
                velocity, heading, vertical_rate, on_ground
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        rows = []
        for data in aircrafts_data:
            timestamp = self._convert_timestamp(data.get("time_position"))
            last_contact = self._convert_timestamp(data.get("last_contact"))
            if timestamp is None and last_contact is None:
                continue
            rows.append((
                data.get("icao24"),
                data.get("callsign"),
                data.get("origin_country"),
                timestamp,
                last_contact,
                data.get("longitude"),
                data.get("latitude"),
                data.get("baro_altitude"),
                data.get("velocity"),
                data.get("heading"),
                data.get("vertical_rate"),
                data.get("on_ground"),
            ))

        try:
            if rows:
                self.cursor.executemany(query, rows)
                self.conn.commit()
                print(f"✅ Вставлено записей о самолётах: {len(rows)}")
        except Exception as e:
            print(f"Ошибка массовой вставки: {e}")
            self.conn.rollback()

    # --- Аналитические методы ---

    def get_countries_and_aeroplanes_count(self):
        """Возвращает количество самолётов по странам."""
        query = """
            SELECT origin_country, COUNT(*)
            FROM aircrafts
            WHERE origin_country IS NOT NULL
            GROUP BY origin_country
            ORDER BY COUNT(*) DESC
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_countries_and_aeroplanes_count: {e}")
            return []

    def get_avg_speed(self):
        """Возвращает среднюю скорость всех самолётов."""
        query = "SELECT AVG(velocity) FROM aircrafts WHERE velocity IS NOT NULL"
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.0
        except Exception as e:
            print(f"Ошибка в get_avg_speed: {e}")
            return 0.0

    def get_aeroplanes_with_higher_speed(self):
        """Возвращает самолёты со скоростью выше средней."""
        avg_speed = self.get_avg_speed()
        if avg_speed == 0.0:
            return []
        query = "SELECT * FROM aircrafts WHERE velocity > %s"
        try:
            self.cursor.execute(query, (avg_speed,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_aeroplanes_with_higher_speed: {e}")
            return []

    def get_aeroplanes_with_keyword(self, keyword):
        """Возвращает самолёты, в позывном которых есть ключевое слово."""
        query = "SELECT * FROM aircrafts WHERE callsign LIKE %s"
        try:
            self.cursor.execute(query, (f"%{keyword}%",))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_aeroplanes_with_keyword: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("🔒 Соединение с БД закрыто.")



