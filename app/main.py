from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI

from app.core.config import load_config
from app.core.database import Model, engine
from app.routers.auth import router as auth_router
from app.routers.authors import router as authors_router
from app.routers.books import router as books_router
from app.routers.notes import router as notes_router
from app.routers.shelf import router as shelf_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    print("Сервер запущен.")
    yield
    print("Выключение сервера.")


config = load_config()

app = FastAPI(
    lifespan=lifespan,
    title="MyLibraryAPI",
    description="API для личной библиотеки",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(books_router)
api_v1_router.include_router(notes_router)
api_v1_router.include_router(shelf_router)
api_v1_router.include_router(authors_router)

app.include_router(api_v1_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
