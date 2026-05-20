from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import User as AiogramUser

from app.bot.handlers.utils import telegram_user_dto
from app.bot.keyboards.reply import main_menu_keyboard
from app.db.database import async_session_factory
from app.services.assessment_service import AssessmentService
from app.services.neural_api import get_neural_api_service


WELCOME_TEXT = (
    "Привет! Я помогу определить твой текущий уровень и собрать маршрут обучения.\n\n"
    "Выбери действие в меню."
)


async def ensure_persistent_menu(
    bot: Bot,
    chat_id: int,
    user_data: AiogramUser,
    refresh_reply_keyboard: bool = False,
) -> int:
    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        user = await service.get_or_create_user(telegram_user_dto(user_data))
        courses = await service.list_user_courses(telegram_user_dto(user_data))
        welcome_message_id = user.welcome_message_id

    reply_markup = main_menu_keyboard(has_courses=bool(courses))

    if welcome_message_id is not None:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=welcome_message_id,
                text=WELCOME_TEXT,
                reply_markup=None,
            )
            return welcome_message_id
        except TelegramBadRequest as error:
            if "message is not modified" in str(error):
                return welcome_message_id

    message = await bot.send_message(
        chat_id=chat_id,
        text=WELCOME_TEXT,
        reply_markup=reply_markup,
    )

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        user = await service.get_or_create_user(telegram_user_dto(user_data))
        await service.set_welcome_message_id(user, message.message_id)

    return message.message_id
