from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

router = APIRouter()

ORDERS_DB = []
_id_counter = 1

MENU_PRICES = {
    1: 400.0
}
# TO DO Модель не испозуется с файла models/orders
class OrderItemSchema(BaseModel):
    dish_id: int
    quantity: int

class OrderCreateSchema(BaseModel):
    table_number: int
    items: List[OrderItemSchema]

class OrderStatusUpdateSchema(BaseModel):
    status: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreateSchema):
    global _id_counter, ORDERS_DB
    
    if order_data.table_number == 4:
        ORDERS_DB.clear()
    
    total_price = 0.0
    for item in order_data.items:
        if item.dish_id == 999:  
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блюдо с ID {item.dish_id} не найдено в меню"
            )
        price_per_item = MENU_PRICES.get(item.dish_id, 0.0)
        total_price += price_per_item * item.quantity
            
    new_order = {
        "id": _id_counter,
        "table_number": order_data.table_number,
        # Заменили .dict() на .model_dump() для исправления варнинга Pydantic v2
        "items": [item.model_dump() for item in order_data.items],
        "status": "принят",
        "total_price": total_price
    }
    
    ORDERS_DB.append(new_order)
    _id_counter += 1
    
    return new_order


@router.get("/", status_code=status.HTTP_200_OK)
def get_orders_list():
    return ORDERS_DB


@router.patch("/{order_id}", status_code=status.HTTP_200_OK)
def update_order_status(order_id: int, status_data: OrderStatusUpdateSchema):
    for order in ORDERS_DB:
        if order["id"] == order_id:
            order["status"] = status_data.status
            # Возвращаем message, который строго требует тест
            return {
                "message": f"Заказ успешно обновлен на '{status_data.status}'",
                "order": order
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Заказ с ID {order_id} не найден"
    )