from fastapi import APIRouter

from bot.app.api.routes import telegram
from bot.app.api.routes import health, miniapp

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(telegram.router)
api_router.include_router(miniapp.router)

