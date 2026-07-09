from pydantic import BaseModel
from typing import List

class OrderItemSchema(BaseModel):
    dish_id: int
    quantity: int

class OrderCreateSchema(BaseModel):
    table_number: int
    items: List[OrderItemSchema]
