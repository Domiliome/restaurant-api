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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Таблица меню
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)
    
    # 2. Таблица заказов для столиков
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'принят',
            total_price REAL NOT NULL DEFAULT 0.0
        )
    """)
    
    # 3. Связующая таблица для блюд в заказе (многие-ко-многим)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            dish_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (dish_id) REFERENCES menu(id)
        )
    """)
    
    # Безопасная проверка количества записей в режиме sqlite3.Row
    cursor.execute("SELECT COUNT(*) as cnt FROM menu")
    row = cursor.fetchone()
    
    if row["cnt"] == 0:
        cursor.executemany("""
            INSERT INTO menu (name, price, category) VALUES (?, ?, ?)
        """, [
            ("Пицца Маргарита", 450.0, "Пицца"),
            ("Салат Цезарь", 380.0, "Салаты")
        ])
        
    conn.commit()
    conn.close()