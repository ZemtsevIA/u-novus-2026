import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import api_router
from app.bot.handlers import register_handlers
from app.bot.loader import bot, dp
from app.core.config import settings
from app.core.logging import setup_logging

handlers_registered = False
logger = logging.getLogger(__name__)


async def run_polling() -> None:
    bot_info = await bot.get_me()
    logger.info("Starting Telegram polling for @%s", bot_info.username)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def setup_webhook() -> None:
    bot_info = await bot.get_me()
    logger.info("Setting Telegram webhook for @%s: %s", bot_info.username, settings.webhook_url)
    await bot.set_webhook(
        url=settings.webhook_url,
        drop_pending_updates=True,
    )


def log_polling_result(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exception = task.exception()
    if exception is not None:
        logger.exception("Telegram polling stopped with an error", exc_info=exception)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global handlers_registered
    setup_logging(settings.debug, settings.neural_api_error_log_path)
    if not handlers_registered:
        register_handlers(dp)
        handlers_registered = True
    polling_task: asyncio.Task | None = None
    if settings.run_polling:
        polling_task = asyncio.create_task(run_polling())
        polling_task.add_done_callback(log_polling_result)
    else:
        await setup_webhook()
    try:
        yield
    finally:
        if polling_task:
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                pass
        await bot.session.close()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router)
