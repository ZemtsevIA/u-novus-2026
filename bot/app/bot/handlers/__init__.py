from aiogram import Dispatcher

from app.bot.handlers import assessment, menu, start


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(assessment.router)

