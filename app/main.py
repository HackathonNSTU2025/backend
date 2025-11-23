from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import get_pool
from app.routes.events import router as events_router
from app.routes.queue_entries import router as queue_entries_router
from app.routes.queues import router as queues_router
from app.routes.stations import router as stations_router
from app.routes.users import router as users_router
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_pool = await get_pool()

    yield

    await app.state.database_pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(events_router)
app.include_router(queue_entries_router)
app.include_router(queues_router)
app.include_router(stations_router)
app.include_router(users_router)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # любые домены
    allow_credentials=True,
    allow_methods=["*"],  # все HTTP-методы
    allow_headers=["*"],  # все заголовки
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
