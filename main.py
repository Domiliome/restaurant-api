from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Restaurant API", description="API для управления меню ресторана")

# Временная база данных в оперативной памяти (сбросится при перезапуске)
menu_db = [
    {"id": 1, "name": "Пицца Маргарита", "price": 450.0, "category": "Пицца"},
    {"id": 2, "name": "Салат Цезарь", "price": 380.0, "category": "Салаты"},
]

# Схема данных для проверки того, что нам отправляет клиент
class DishCreate(BaseModel):
    name: str
    price: float
    category: str

# 1. Получить всё меню
@app.get("/menu", response_model=List[dict])
def get_menu():
    return menu_db

# 2. Получить конкретное блюдо по ID
@app.get("/menu/{dish_id}")
def get_dish(dish_id: int):
    for dish in menu_db:
        if dish["id"] == dish_id:
            return dish
    raise HTTPException(status_code=404, detail="Блюдо не найдено")

# 3. Добавить новое блюдо в меню
@app.post("/menu", status_code=201)
def create_dish(dish: DishCreate):
    # Генерируем новый ID на основе максимального существующего
    new_id = max([d["id"] for d in menu_db]) + 1 if menu_db else 1
    new_dish = {
        "id": new_id,
        "name": dish.name,
        "price": dish.price,
        "category": dish.category
    }
    menu_db.append(new_dish)
    return new_dish

# 4. Удалить блюдо из меню
@app.delete("/menu/{dish_id}")
def delete_dish(dish_id: int):
    for index, dish in enumerate(menu_db):
        if dish["id"] == dish_id:
            deleted_dish = menu_db.pop(index)
            return {"message": f"Блюдо '{deleted_dish['name']}' успешно удалено"}
    raise HTTPException(status_code=404, detail="Блюдо не найдено")