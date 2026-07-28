import psycopg2
from psycopg2.extras import RealDictCursor

class DBManager:
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(self, dbname, user, password, host='localhost', port=5432):
        """Инициализирует подключение к базе данных."""
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

    def get_countries_and_aeroplanes_count(self):
        """
        Возвращает список стран и количество самолётов в их воздушных пространствах.
        Использует JOIN и фильтрацию по радиусу вокруг центра страны.
        """
        query = """
            SELECT c.name, COUNT(a.icao24) AS total_aircrafts
            FROM countries c
            LEFT JOIN aircraft a 
                ON a.latitude BETWEEN (c.latitude - c.radius_km / 111) AND (c.latitude + c.radius_km / 111)
                AND a.longitude BETWEEN (c.longitude - c.radius_km / 111) AND (c.longitude + c.radius_km / 111)
            GROUP BY c.id, c.name
            ORDER BY total_aircrafts DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_all_aeroplanes(self):
        """Возвращает все записи о воздушных судах из таблицы aircraft."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM aircraft;")
            return cur.fetchall()

    def get_avg_speed(self):
        """Вычисляет и возвращает среднюю скорость всех самолётов."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT AVG(velocity) AS average_speed FROM aircraft;")
            result = cur.fetchone()
            return result['average_speed'] if result else 0.0

    def get_aeroplanes_with_higher_speed(self):
        """
        Возвращает список самолётов, у которых скорость выше средней.
        Использует подзапрос для расчёта средней скорости.
        """
        query = """
            SELECT * FROM aircraft 
            WHERE velocity > (SELECT AVG(velocity) FROM aircraft);
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword):
        """
        Ищет самолёты, в позывном которых содержится указанная подстрока.
        Поиск регистронезависимый (ILIKE).
        """
        param = f"%{keyword}%"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM aircraft WHERE callsign ILIKE %s;", (param,))
            return cur.fetchall()

    def close(self):
        """Закрывает соединение с базой данных."""
        self.conn.close()