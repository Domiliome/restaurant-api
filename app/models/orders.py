from pydantic import BaseModel, Field
from typing import List

# Схема для конкретного элемента в заказе
class OrderItemCreate(BaseModel):
    dish_id: int = Field(..., description="ID блюда из меню")
    quantity: int = Field(..., gt=0, description="Количество порций (больше 0)")

# Схема для создания самого заказа (её ищет роутер)
class OrderCreate(BaseModel):
    table_number: int = Field(..., gt=0, description="Номер столика")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Список блюд в заказе")

# Схема для обновления статуса заказа (её ищет роутер)
class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="Новый статус: принят, готовится, подан, оплачен")
