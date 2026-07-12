import os
import pytest
from fastapi.testclient import TestClient

# 1. Переопределяем путь к базе данных ДО импорта приложения
import app.database as database
TEST_DB_PATH = "test_restaurant.db"
database.DB_PATH = TEST_DB_PATH

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
    """Перед каждым тестом очищает таблицы и создает стартовые данные"""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM menu")
    

    cursor.execute(
        "INSERT INTO menu (id, name, price, category) VALUES (?, ?, ?, ?)", 
        (1, "Тестовая пицца", 400.0, "Пицца")
    )
    conn.commit()
    conn.close()


client = TestClient(app)

# --- ТЕСТЫ МЕНЮ ---

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


# --- ТЕСТЫ ЗАКАЗОВ (ORDERS) ---

def test_create_order_success():
    """Успешное создание заказа со стоимостью на основе цен из меню"""
    order_data = {
        "table_number": 3,
        "items": [
            {"dish_id": 1, "quantity": 2} # 2 пиццы по 400 = 800
        ]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["table_number"] == 3
    assert data["status"] == "принят"
    assert data["total_price"] == 800.0 
    assert "id" in data

def test_create_order_dish_not_found():
    """Заказ должен вернуть 404, если блюда нет в меню"""
    order_data = {
        "table_number": 2,
        "items": [
            {"dish_id": 999, "quantity": 1} # ID 999 не существует
        ]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 404
    assert "не найдено в меню" in response.json()["detail"]

def test_get_orders_list():
    """Проверка получения списка всех заказов"""
    # Сначала создаем один заказ
    client.post("/orders/", json={"table_number": 4, "items": [{"dish_id": 1, "quantity": 1}]})
    
    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["table_number"] == 4

def test_update_order_status():
    """Проверка успешной смены статуса заказа через PATCH"""
    # Создаем заказ
    create_res = client.post("/orders/", json={"table_number": 1, "items": [{"dish_id": 1, "quantity": 1}]})
    order_id = create_res.json()["id"]
    
    # Меняем статус
    update_data = {"status": "готовится"}
    response = client.patch(f"/orders/{order_id}", json=update_data)
    assert response.status_code == 200
    assert "успешно обновлен на 'готовится'" in response.json()["message"]

def test_pay_order_success_and_block_duplicate():
    """Проверяем успешную оплату и блокировку повторного закрытия чека"""
    # 1. Создаем заказ
    create_res = client.post("/orders/", json={"table_number": 2, "items": [{"dish_id": 1, "quantity": 2}]})
    order_id = create_res.json()["id"]
    
    # 2. Оплачиваем заказ
    pay_response = client.post(f"/orders/{order_id}/pay")
    assert pay_response.status_code == 200
    assert "успешно оплачен и закрыт" in pay_response.json()["message"]
    assert "ИТОГО К ОПЛАТЕ" in pay_response.json()["receipt"]
    
    # 3. Пробуем оплатить его ЕЩЁ РАЗ (должна быть ошибка 400)
    duplicate_pay = client.post(f"/orders/{order_id}/pay")
    assert duplicate_pay.status_code == 400
    assert "уже был оплачен ранее" in duplicate_pay.json()["detail"]
