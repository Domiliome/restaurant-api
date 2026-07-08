import sqlite3

# Файл базы данных будет создаваться в корне проекта
DB_PATH = "restaurant.db"

def get_db_connection():
    # Создаем подключение к файлу SQLite
    conn = sqlite3.connect(DB_PATH)
    # Включаем режим Row, чтобы получать строки из БД в виде удобных словарей
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Создаем таблицу меню, если её ещё нет
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)
    
    # Наполняем базу начальными данными, если она абсолютно пустая
    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO menu (name, price, category) VALUES (?, ?, ?)
        """, [
            ("Пицца Маргарита", 450.0, "Пицца"),
            ("Салат Цезарь", 380.0, "Салаты")
        ])
    conn.commit()
    conn.close()