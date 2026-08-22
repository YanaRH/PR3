import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class DBManager:

    def __init__(self):
        """
        Инициализация соединения с базой данных.
        КРИТЕРИЙ 2: Используем переменную окружения, а не хардкод.
        """
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("Ошибка: в файле .env не задана переменная DATABASE_URL!")

        try:
            self.conn = psycopg2.connect(db_url)
            self.cursor = self.conn.cursor()
            print("✅ Успешное подключение к базе данных.")

            # КРИТЕРИЙ 1: Автоматическое создание таблиц при старте
            self._ensure_tables()

        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise e

    def _ensure_tables(self):
        """
        КРИТЕРИЙ 1: Создаёт таблицы, если они ещё не существуют.
        Вызывается автоматически в __init__.
        """
        # Таблица стран
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                coordinates VARCHAR(100)
            );
        """)

        # Таблица самолётов
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS aircrafts (
                id SERIAL PRIMARY KEY,
                country_id INTEGER,
                registration VARCHAR(50),
                callsign VARCHAR(20),
                x DOUBLE PRECISION,
                y DOUBLE PRECISION,
                altitude DOUBLE PRECISION,
                velocity DOUBLE PRECISION,
                heading DOUBLE PRECISION,
                vertical_rate DOUBLE PRECISION,
                on_ground BOOLEAN,
                time_position TIMESTAMP  -- КРИТЕРИЙ 4: тип TIMESTAMP
            );
        """)
        self.conn.commit()
        print("✅ Таблицы проверены/созданы.")

    @staticmethod
    def _convert_timestamp(raw_time):
        """
        КРИТЕРИЙ 4: Безопасная конвертация Unix-времени в datetime.
        Обрабатывает и секунды, и миллисекунды (если число > 2 млрд).
        """
        if raw_time is None:
            return None

        if isinstance(raw_time, datetime):
            return raw_time

        if isinstance(raw_time, (int, float)):
            # Если число больше 2147483647 — это миллисекунды
            if raw_time > 2147483647:
                return datetime.fromtimestamp(raw_time / 1000.0)
            else:
                # Иначе это секунды
                return datetime.fromtimestamp(raw_time)

        return None

    def add_country(self, name, coordinates):
        query = """
        INSERT INTO countries (name, coordinates)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING
        RETURNING id;
        """
        try:
            self.cursor.execute(query, (name, coordinates))
            self.conn.commit()
            result = self.cursor.fetchone()
            return result if result else None
        except Exception as e:
            print(f"Ошибка при добавлении страны {name}: {e}")
            self.conn.rollback()
            return None

    def add_aircraft(self, data):
        """
        Добавляет один самолёт.
        КРИТЕРИЙ 4: Использует _convert_timestamp для правильной вставки времени.
        """
        if not data.get('time_position'):
            return

        timestamp = self._convert_timestamp(data['time_position'])
        if timestamp is None:
            return  # Пропускаем, если не удалось конвертировать

        table_name = 'aircrafts'

        query = f"""
        INSERT INTO {table_name} (
            country_id, registration, callsign, x, y, altitude,
            velocity, heading, vertical_rate, on_ground, time_position
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            self.cursor.execute(query, (
                data.get('country_id'),
                data.get('registration'),
                data.get('callsign'),
                data.get('x'),
                data.get('y'),
                data.get('altitude'),
                data.get('velocity'),
                data.get('heading'),
                data.get('vertical_rate'),
                data.get('on_ground'),
                timestamp
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при добавлении самолета {data.get('callsign')}: {e}")
            self.conn.rollback()

    def insert_aircrafts(self, aircrafts_data):
        """
        Массовая вставка самолётов.
        КРИТЕРИЙ 4: Конвертирует время для каждой записи.
        """
        if not aircrafts_data:
            print("⚠️ Нет данных для вставки в таблицу aircrafts.")
            return

        table_name = 'aircrafts'
        query = f"""
        INSERT INTO {table_name} (
            country_id, registration, callsign, x, y, altitude,
            velocity, heading, vertical_rate, on_ground, time_position
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data_to_insert = []
        for data in aircrafts_data:
            if not data.get('time_position'):
                continue

            timestamp = self._convert_timestamp(data['time_position'])
            if timestamp is None:
                continue  # Пропускаем эту запись, если время не конвертировалось

            row = (
                data.get('country_id'),
                data.get('registration'),
                data.get('callsign'),
                data.get('x'),
                data.get('y'),
                data.get('altitude'),
                data.get('velocity'),
                data.get('heading'),
                data.get('vertical_rate'),
                data.get('on_ground'),
                timestamp
            )
            data_to_insert.append(row)

        try:
            if data_to_insert:
                self.cursor.executemany(query, data_to_insert)
                self.conn.commit()
                print(f"✅ Успешно вставлено {len(data_to_insert)} записей.")
        except Exception as e:
            print(f"Ошибка массовой вставки: {e}")
            self.conn.rollback()

    # --- Аналитические методы (оставлены как в твоём исходном коде) ---

    def get_countries_and_aeroplanes_count(self):
        query = """
        SELECT c.name, COUNT(a.id) 
        FROM countries c
        LEFT JOIN aircrafts a ON c.id = a.country_id
        GROUP BY c.name
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_countries_and_aeroplanes_count: {e}")
            return []

    def get_avg_speed(self):
        query = "SELECT AVG(velocity) FROM aircrafts"
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.0
        except Exception as e:
            print(f"Ошибка в get_avg_speed: {e}")
            return 0.0

    def get_aeroplanes_with_higher_speed(self):
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
        query = "SELECT * FROM aircrafts WHERE callsign LIKE %s"
        try:
            self.cursor.execute(query, (f'%{keyword}%',))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_aeroplanes_with_keyword: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("🔒 Соединение с БД закрыто.")



