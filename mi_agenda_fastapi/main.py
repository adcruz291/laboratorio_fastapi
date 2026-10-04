from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import src.models  # noqa: F401  (registra las tablas)
from src.database import init_db
from src.middlewares.timer import TimerMiddleware
from src.routers import agenda, auth, views


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Mi Agenda", lifespan=lifespan)
app.add_middleware(TimerMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(agenda.router)
app.include_router(views.router)
