from fastapi import APIRouter, HTTPException, status
from typing import List
# Используем схемы из файла моделей
from app.models.orders import OrderCreate, OrderStatusUpdate
from app.database import get_db_connection

router = APIRouter()

# 1. Создать новый заказ с сохранением в SQLite
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_price = 0.0
    verified_items = []
    
    # Проверяем, существуют ли блюда в меню и динамически считаем сумму
    for item in order_data.items:
        cursor.execute("SELECT price, name FROM menu WHERE id = ?", (item.dish_id,))
        dish = cursor.fetchone()
        if dish is None:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блюдо с ID {item.dish_id} не найдено в меню"
            )
        
        total_price += dish["price"] * item.quantity
        verified_items.append((item.dish_id, item.quantity, dish["name"], dish["price"]))
        
    # Сохраняем сам заказ
    cursor.execute(
        "INSERT INTO orders (table_number, status, total_price) VALUES (?, 'принят', ?)",
        (order_data.table_number, total_price)
    )
    order_id = cursor.lastrowid
    
    # Сохраняем позиции заказа в связующую таблицу
    response_items = []
    for dish_id, quantity, name, price in verified_items:
        cursor.execute(
            "INSERT INTO order_items (order_id, dish_id, quantity) VALUES (?, ?, ?)",
            (order_id, dish_id, quantity)
        )
        response_items.append({
            "name": name,
            "price": price,
            "quantity": quantity
        })
        
    conn.commit()
    conn.close()
    
    return {
        "id": order_id,
        "table_number": order_data.table_number,
        "status": "принят",
        "total_price": total_price,
        "items": response_items
    }


# 2. Получить список всех заказов с детальным составом блюд (JOIN)
@router.get("/", status_code=status.HTTP_200_OK)
def get_orders_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders")
    orders_rows = cursor.fetchall()
    
    detailed_orders = []
    for order in orders_rows:
        order_dict = dict(order)
        
        # Подтягиваем названия и цены блюд из таблицы menu
        cursor.execute("""
            SELECT m.name, m.price, oi.quantity 
            FROM order_items oi
            JOIN menu m ON oi.dish_id = m.id
            WHERE oi.order_id = ?
        """, (order_dict["id"],))
        
        order_dict["items"] = [dict(item) for item in cursor.fetchall()]
        detailed_orders.append(order_dict)
        
    conn.close()
    return detailed_orders


# 3. Изменить статус заказа
@router.patch("/{order_id}", status_code=status.HTTP_200_OK)
def update_order_status(order_id: int, status_data: OrderStatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден"
        )
        
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status_data.status, order_id))
    conn.commit()
    conn.close()
    
    return {
        "message": f"Статус заказа #{order_id} успешно обновлен на '{status_data.status}'"
    }


# 4. Закрытие (оплата) заказа и печать чека
@router.post("/{order_id}/pay", status_code=status.HTTP_200_OK)
def pay_and_print_receipt(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверяем существование заказа
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order_row = cursor.fetchone()
    
    if order_row is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден"
        )
        
    order = dict(order_row)
    if order["status"] == "оплачен":
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот заказ уже был оплачен ранее"
        )
        
    # Собираем все позиции этого заказа для чека
    cursor.execute("""
        SELECT m.name, m.price, oi.quantity 
        FROM order_items oi
        JOIN menu m ON oi.dish_id = m.id
        WHERE oi.order_id = ?
    """, (order_id,))
    items = [dict(item) for item in cursor.fetchall()]
    
    # Меняем статус заказа на 'оплачен'
    cursor.execute("UPDATE orders SET status = 'оплачен' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    
    # Генерируем красивый текстовый чек
    receipt_lines = [
        "================================",
        "       РЕСТОРАН 'FAST FLAVORS'  ",
        "================================",
        f"Заказ №:       {order['id']}",
        f"Столик №:      {order['table_number']}",
        f"Статус:        ОПЛАЧЕНО",
        "--------------------------------"
    ]
    
    for item in items:
        item_total = item['price'] * item['quantity']
        receipt_lines.append(f"{item['name']}")
        receipt_lines.append(f"  {item['quantity']} шт. х {item['price']:.2f} = {item_total:.2f} руб.")
        
    receipt_lines.extend([
        "--------------------------------",
        f"ИТОГО К ОПЛАТЕ:  {order['total_price']:.2f} руб.",
        "================================",
        "    Спасибо за ваш визит!       ",
        "================================"
    ])
    
    text_receipt = "\n".join(receipt_lines)
    
    return {
        "message": f"Заказ #{order_id} успешно оплачен и закрыт",
        "receipt": text_receipt
    }
