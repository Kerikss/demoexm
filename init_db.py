import sqlite3
import os
from config import DB_PATH


def init_database():
    # Удаляем старую базу данных, если она существует
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Старая база данных {DB_PATH} удалена.")

    # Создаём новую БД и выполняем SQL-скрипт
    conn = sqlite3.connect(DB_PATH)
    with open('SQL Запрос.txt', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    conn.executescript(sql_script)
    conn.commit()
    conn.close()
    print("База данных успешно инициализирована из SQL-скрипта.")


if __name__ == '__main__':
    init_database()