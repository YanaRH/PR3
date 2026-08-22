import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect

load_dotenv()


def check_tables():
    engine = create_engine(os.getenv('DATABASE_URL'))
    inspector = inspect(engine)

    print("Доступные таблицы:")
    for table in inspector.get_table_names():
        print(f"- {table}")


if __name__ == "__main__":
    check_tables()