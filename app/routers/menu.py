from fastapi import APIRouter, HTTPException
from app.models.menu import DishCreate
from app.database import get_db_connection

router = APIRouter()

# 1. Получить всё меню
@router.get("/")
def get_menu():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    dishes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return dishes

# 2. Получить конкретное блюдо по ID
@router.get("/{dish_id}")
def get_dish(dish_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu WHERE id = ?", (dish_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return dict(row)

# 3. Добавить новое блюдо в меню
@router.post("/", status_code=201)
def create_dish(dish: DishCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu (name, price, category) VALUES (?, ?, ?)",
        (dish.name, dish.price, dish.category)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return {"id": new_id, "name": dish.name, "price": dish.price, "category": dish.category}

# 4. Удалить блюдо из меню
@router.delete("/{dish_id}")
def delete_dish(dish_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM menu WHERE id = ?", (dish_id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    
    cursor.execute("DELETE FROM menu WHERE id = ?", (dish_id,))
    conn.commit()
    conn.close()
    
    return {"message": f"Блюдо '{row['name']}' успешно удалено"}