from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.handlers.cleanup import cleanup_bot_messages
from app.bot.handlers.persistent_menu import ensure_persistent_menu
from app.bot.handlers.utils import telegram_user_dto
from app.db.database import async_session_factory
from app.services.assessment_service import AssessmentService
from app.services.neural_api import get_neural_api_service

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    if message.from_user is None:
        return

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        user = await service.get_or_create_user(telegram_user_dto(message.from_user))
        cleanup_ids = await service.pop_user_roadmap_messages(user.id)
        active_assessment = await service.get_active_assessment(user)
        if active_assessment is not None:
            cleanup_ids.extend(await service.pop_bot_messages(active_assessment.id))

    await cleanup_bot_messages(message.bot, message.chat.id, cleanup_ids)
    await ensure_persistent_menu(
        message.bot,
        message.chat.id,
        message.from_user,
        refresh_reply_keyboard=True,
    )
