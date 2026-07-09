from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db

from app.routers.menu import router as menu_router
from app.routers.orders import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск базы данных при старте приложения
    init_db()
    yield

app = FastAPI(
    title="Restaurant API", 
    description="",
    lifespan=lifespan
)

app.include_router(menu_router, prefix="/menu", tags=["Menu"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])  # <-- 2. Подключаем роутер

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Добро пожаловать в API ресторана!"}
