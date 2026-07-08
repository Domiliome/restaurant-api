from pydantic import BaseModel, Field

# Схема данных для валидации при создании нового блюда
class DishCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Название блюда")
    price: float = Field(..., gt=0, description="Цена блюда (должна быть больше нуля)")
    category: str = Field(..., min_length=2, max_length=50, description="Категория (например, Пицца, Супы)")

    # Пример данных для автодокументации Swagger UI
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Борщ",
                "price": 320.0,
                "category": "Супы"
            }
        }
    }