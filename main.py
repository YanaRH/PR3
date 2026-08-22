import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, DatabaseError


# Определяем корень проекта (папку, где лежит main.py)
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

# Загружаем переменные СТРОГО из этого файла
load_dotenv(dotenv_path=ENV_FILE)

print(f"📂 Путь к файлу .env: {ENV_FILE}")
print(f"✅ Файл .env существует: {ENV_FILE.exists()}")
print(f"🔑 DB_PASSWORD из env: {os.getenv('DB_PASSWORD')}")  # Отладка: сразу видим, что загрузилось
print("-" * 40)

# Импорты из ваших локальных модулей
try:
    from models import Base
    # Раскомментируйте остальные импорты, если они нужны для работы main()
    # from data_fetch.countries import get_country_coordinates
    # from data_fetch.opensky import get_aircrafts_data
    # from db_manager import DBManager
except ImportError as e:
    print(f"❌ Ошибка импорта локальных модулей: {e}")
    sys.exit(1)


def init_database():
    """
    Инициализирует подключение к БД.
    Жестко проверяет наличие всех критических переменных.
    """
    print("🔍 Проверка переменных окружения...")

    # Получаем значения. ИСПРАВЛЕНО: правильный ключ 'DB_PASSWORD'
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')  # ✅ Теперь берем переменную, а не строку '5432'
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'air_project')

    # --- Строгая валидация ---
    missing_vars = []
    if not db_user:
        missing_vars.append('DB_USER')
    if not db_password:
        missing_vars.append('DB_PASSWORD')
    if not db_host:
        missing_vars.append('DB_HOST')
    if not db_name:
        missing_vars.append('DB_NAME')

    if missing_vars:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: Не найдены следующие переменные в файле .env: {', '.join(missing_vars)}")
        print("💡 Проверьте файл .env в папке проекта.")
        print("💡 Убедитесь, что в значениях нет русских букв и лишних пробелов.")
        raise ValueError(f"Отсутствуют переменные: {', '.join(missing_vars)}")

    # Формируем URL подключения
    # client_encoding=utf8 добавлен для защиты от ошибок декодирования
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?client_encoding=utf8"

    print(f"✅ Попытка подключения к БД: {db_user}@{db_host}/{db_name}")

    try:
        engine = create_engine(database_url)

        # Пробуем установить соединение (ping), чтобы сразу увидеть ошибку пароля
        with engine.connect() as conn:
            print("✅ Соединение с PostgreSQL успешно установлено!")

        # Создаем таблицы, если их нет (это безопасно, если таблицы уже существуют)
        print("🗄️ Проверка и создание таблиц...")
        Base.metadata.create_all(engine)
        print("✅ Таблицы проверены/созданы.")

        return engine

    except OperationalError as e:
        # Эта ошибка возникнет, если пароль неверен или сервер недоступен
        print(f"❌ Ошибка аутентификации или подключения к БД: {e}")
        print("💡 Если видите 'password authentication failed', значит .env читается верно, но пароль не подходит.")
        raise
    except DatabaseError as e:
        print(f"❌ Общая ошибка базы данных: {e}")
        raise
    except Exception as e:
        print(f"❌ Неожиданная ошибка при инициализации БД: {e}")
        raise


def main():
    """
    Основная функция приложения.
    """
    try:
        # 1. Инициализация БД
        engine = init_database()

        # 2. Здесь должна быть ваша основная логика
        # Например:
        # db_manager = DBManager(engine)
        # data = get_aircrafts_data()
        # db_manager.save_aircrafts(data)

        print("🚀 Приложение запущено и готово к работе!")

    except Exception as e:
        print(f"💥 Критическая ошибка приложения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

