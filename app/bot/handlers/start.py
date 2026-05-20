from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.bot.keyboards.reply import main_menu_keyboard
from app.bot.handlers.utils import telegram_user_dto
from app.db.database import async_session_factory
from app.services.assessment_service import AssessmentService
from app.services.neural_api import get_neural_api_service

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    if message.from_user is None:
        return

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        assessment = await service.start_assessment(telegram_user_dto(message.from_user))

    intro_message = await message.answer(
        "Привет! Я помогу определить твой текущий уровень.\nЧему ты хочешь научиться?",
        reply_markup=main_menu_keyboard(),
    )
