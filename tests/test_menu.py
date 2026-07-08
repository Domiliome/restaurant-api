import os
import pytest
from fastapi.testclient import TestClient

# 1. Переопределяем путь к базе данных ДО импорта приложения
import app.database as database
TEST_DB_PATH = "test_restaurant.db"
database.DB_PATH = TEST_DB_PATH

# 2. Теперь безопасно импортируем само приложение
from app.main import app

@pytest.fixture(scope="session", autouse=True)
def manage_test_db():
    """Создает тестовую БД перед запуском тестов и удаляет её после завершения"""
    database.init_db()
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture(autouse=True)
def clean_each_test():
    """Перед каждым тестом очищает таблицу меню и добавляет одно тестовое блюдо"""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu")
    # Жестко фиксируем ID=1 для тестов получения и удаления
    cursor.execute(
        "INSERT INTO menu (id, name, price, category) VALUES (?, ?, ?, ?)", 
        (1, "Тестовая пицца", 400.0, "Пицца")
    )
    conn.commit()
    conn.close()

# Создаем тестового клиента
client = TestClient(app)

# --- Тест-кейсы ---

def test_get_menu():
    response = client.get("/menu/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Тестовая пицца"

def test_create_dish():
    new_dish = {"name": "Борщ", "price": 320.0, "category": "Супы"}
    response = client.post("/menu/", json=new_dish)
    assert response.status_code == 201
    assert response.json()["name"] == "Борщ"

def test_get_dish_by_id():
    response = client.get("/menu/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Тестовая пицца"

def test_delete_dish():
    response = client.delete("/menu/1")
    assert response.status_code == 200
    assert "успешно удалено" in response.json()["message"]