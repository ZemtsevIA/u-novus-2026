from aiogram import Dispatcher

from bot.app.bot.handlers import start
from bot.app.bot.handlers import assessment, menu


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(assessment.router)

