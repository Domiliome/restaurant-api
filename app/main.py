from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db

from app.routers.menu import router as menu_router

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
# prefix="/menu" означает, что все эндпоинты внутри этого роутера автоматически получат этот префикс
app.include_router(menu_router, prefix="/menu", tags=["Menu"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Добро пожаловать в API ресторана!"}