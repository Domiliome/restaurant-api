from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db

from app.routers.menu import router as menu_router
from app.routers.orders import router as orders_router  # <-- 1. Импортируем новый роутер

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск базы данных при старте приложения
    init_db()
    yield

app = FastAPI(
    title="Restaurant API", 
    description="Профессиональное API для управления меню ресторана",
    lifespan=lifespan
)

# Подключаем маршруты для работы с меню
app.include_router(menu_router, prefix="/menu", tags=["Menu"])

# Подключаем маршруты для работы с заказами
# Префикс "/orders" сопоставит эндпоинты с запросами тестов (/orders/)
app.include_router(orders_router, prefix="/orders", tags=["Orders"])  # <-- 2. Подключаем роутер

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Добро пожаловать в API ресторана!"}
