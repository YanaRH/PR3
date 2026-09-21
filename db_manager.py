import psycopg2
from datetime import datetime

from config.settings import DB_CONFIG


class DBManager:
    """
    Менеджер базы данных.
    Реализует все требования ТЗ: создание схемы с FK, миграция, CRUD, аналитика.
    """

    def __init__(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ Подключение к БД установлено.")
            self._ensure_tables()
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise

    def _ensure_tables(self):
        """
        Создает таблицы и гарантирует наличие внешнего ключа country_id -> countries(id).
        Выполняет миграцию для существующих баз данных без потери данных.
        """
        # 1. Таблица стран
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                radius_km DOUBLE PRECISION DEFAULT 800.0
            );
        """)

        # 2. Таблица самолетов (с декларацией FK для новых БД)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS aircrafts (
                id SERIAL PRIMARY KEY,
                country_id INTEGER REFERENCES countries(id),
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

        # 3. Миграция для старых БД (добавление колонки и FK)
        self.cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'aircrafts' AND column_name = 'country_id';
        """)
        has_country_id = self.cursor.fetchone() is not None

        if not has_country_id:
            print("⚠️ Выполняем миграцию: добавляем country_id и FK...")
            try:
                self.cursor.execute("ALTER TABLE aircrafts ADD COLUMN country_id INTEGER;")
                self.cursor.execute("""
                    ALTER TABLE aircrafts 
                    ADD CONSTRAINT fk_aircrafts_country 
                    FOREIGN KEY (country_id) REFERENCES countries(id);
                """)
                self.conn.commit()
                print("✅ Миграция завершена.")
            except Exception as e:
                print(f"❌ Ошибка миграции: {e}")
                self.conn.rollback()
        else:
            # Проверка наличия самого ограничения FK
            self.cursor.execute("""
                SELECT constraint_name FROM information_schema.table_constraints
                WHERE table_name = 'aircrafts' AND constraint_type = 'FOREIGN KEY'
                AND constraint_name LIKE '%fk_aircrafts_country%';
            """)
            if not self.cursor.fetchone():
                print("⚠️ Добавляем ограничение внешнего ключа...")
                try:
                    self.cursor.execute("""
                        ALTER TABLE aircrafts 
                        ADD CONSTRAINT fk_aircrafts_country 
                        FOREIGN KEY (country_id) REFERENCES countries(id);
                    """)
                    self.conn.commit()
                except Exception as e:
                    print(f"❌ Ошибка добавления FK: {e}")
                    self.conn.rollback()

        self.conn.commit()
        print("✅ Схема БД актуальна.")

    @staticmethod
    def _convert_timestamp(raw_time):
        if raw_time is None: return None
        if isinstance(raw_time, datetime): return raw_time
        if isinstance(raw_time, (int, float)):
            if raw_time > 2147483647: return datetime.fromtimestamp(raw_time / 1000.0)
            return datetime.fromtimestamp(raw_time)
        return None

    def save_countries(self, countries_data):
        if not countries_data: return
        query = """
            INSERT INTO countries (name, latitude, longitude, radius_km)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                radius_km = EXCLUDED.radius_km;
        """
        try:
            for c in countries_data:
                self.cursor.execute(query, (c["name"], c["lat"], c["lon"], 800.0))
            self.conn.commit()
            print(f"✅ Сохранено стран: {len(countries_data)}")
        except Exception as e:
            print(f"❌ Ошибка сохранения стран: {e}")
            self.conn.rollback()

    def save_aircrafts(self, aircrafts_data):
        if not aircrafts_data:
            print("⚠️ Нет данных для вставки.")
            return

        query = """
            INSERT INTO aircrafts (
                country_id, icao24, callsign, origin_country, time_position,
                last_contact, longitude, latitude, baro_altitude,
                velocity, heading, vertical_rate, on_ground
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # ИСПРАВЛЕНО: rows =
        rows = []

        for data in aircrafts_data:
            ts = self._convert_timestamp(data.get("time_position"))
            lc = self._convert_timestamp(data.get("last_contact"))
            if ts is None and lc is None: continue

            rows.append((
                None, data.get("icao24"), data.get("callsign"), data.get("origin_country"),
                ts, lc, data.get("longitude"), data.get("latitude"),
                data.get("baro_altitude"), data.get("velocity"), data.get("heading"),
                data.get("vertical_rate"), data.get("on_ground")
            ))

        try:
            if rows:
                self.cursor.executemany(query, rows)
                self.conn.commit()
                print(f"✅ Вставлено записей: {len(rows)}")
        except Exception as e:
            print(f"❌ Ошибка вставки: {e}")
            self.conn.rollback()

    # --- МЕТОДЫ ИЗ ТЗ (АНАЛИТИКА) ---

    def get_countries_and_aeroplanes_count(self):
        """
        ТЗ: Получает список всех стран и количество самолетов в их воздушных пространствах.
        Использует JOIN и GROUP BY.
        """
        query = """
            SELECT c.name, COUNT(a.id) AS total_aircrafts
            FROM countries c
            LEFT JOIN aircrafts a ON c.id = a.country_id
            GROUP BY c.id, c.name
            ORDER BY total_aircrafts DESC;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка в get_countries_and_aeroplanes_count: {e}")
            return

    def get_all_aeroplanes(self):
        """
        ТЗ: Получает список всех воздушных судов.
        """
        query = "SELECT * FROM aircrafts"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка в get_all_aeroplanes: {e}")
            return

    def get_avg_speed(self):
        """
        ТЗ: Получает среднюю скорость по самолетам.
        """
        query = "SELECT AVG(velocity) FROM aircrafts WHERE velocity IS NOT NULL"
        try:
            self.cursor.execute(query)
            res = self.cursor.fetchone()
            return float(res) if res and res is not None else 0.0
        except Exception as e:
            print(f"❌ Ошибка в get_avg_speed: {e}")
            return 0.0

    def get_aeroplanes_with_higher_speed(self):
        """
        ТЗ: Получает список самолетов, у которых скорость выше средней.
        """
        avg = self.get_avg_speed()
        if avg == 0.0: return

        query = "SELECT * FROM aircrafts WHERE velocity > %s"
        try:
            self.cursor.execute(query, (avg,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка в get_aeroplanes_with_higher_speed: {e}")
            return

    def get_aeroplanes_with_keyword(self, keyword):
        """
        ТЗ: Получает список самолетов, в позывном которых есть символы.
        """
        if not keyword: return
        query = "SELECT * FROM aircrafts WHERE callsign LIKE %s"
        try:
            self.cursor.execute(query, (f"%{keyword}%",))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка в get_aeroplanes_with_keyword: {e}")
            return

            # Дополнительный метод для детального просмотра (JOIN) - опционально, но полезно

    def get_aircrafts_with_country_info(self):
        """
        Возвращает самолеты с названием страны (JOIN).
        """
        query = """
            SELECT c.name AS country_name, a.*
            FROM aircrafts a
            LEFT JOIN countries c ON a.country_id = c.id
            LIMIT 100;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка в get_aircrafts_with_country_info: {e}")
            return

    def close(self):
        if self.conn:
            self.conn.close()
            print("🔒 Соединение закрыто.")


