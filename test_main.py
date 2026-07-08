from fastapi.testclient import TestClient
# Импортируем наше приложение из файла main.py
from main import app

# Создаем клиента для отправки запросов
client = TestClient(app)

# 1. Тест получения всего меню
def test_get_menu():
    response = client.get("/menu")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# 2. Тест добавления нового блюда
def test_create_dish():
    new_dish = {
        "name": "Борщ",
        "price": 320.0,
        "category": "Супы"
    }
    response = client.post("/menu", json=new_dish)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Борщ"
    assert data["price"] == 320.0
    assert "id" in data

# 3. Тест получения ошибки 404 для несуществующего блюда
def test_get_non_existent_dish():
    response = client.get("/menu/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Блюдо не найдено"
