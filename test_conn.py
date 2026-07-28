import psycopg2
from config.settings import DB_DSN

try:
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("✅ Успех! Версия PostgreSQL:", cur.fetchone())
    conn.close()
except Exception as e:
    print("❌ Ошибка подключения:", e)
