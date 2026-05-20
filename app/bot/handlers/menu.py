from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from app.bot.handlers.cleanup import cleanup_bot_messages
from app.bot.handlers.utils import format_courses_page, telegram_user_dto
from app.bot.keyboards.inline import courses_webapp_keyboard
from app.db.database import async_session_factory
from app.services.assessment_service import AssessmentService
from app.services.course_service import CourseService
from app.services.neural_api import get_neural_api_service

router = Router()


async def safe_delete_user_message(message: Message) -> None:
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


@router.message(F.text.in_({"Пройти оценку", "Пройти новую оценку"}))
async def menu_start_assessment(message: Message) -> None:
    if message.from_user is None:
        return

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())

        user = await service.get_or_create_user(telegram_user_dto(message.from_user))

        cleanup_ids: list[int] = []

        active_assessment = await service.get_active_assessment(user)
        if active_assessment is not None:
            cleanup_ids.extend(await service.pop_bot_messages(active_assessment.id))

        cleanup_ids.extend(await service.pop_user_roadmap_messages(user.id))

        assessment = await service.start_assessment(telegram_user_dto(message.from_user))

    try:
        await message.delete()
    except TelegramBadRequest as e:
        print(f"Не удалось удалить сообщение пользователя: {e}")

    print("cleanup_ids:", cleanup_ids)

    await cleanup_bot_messages(message.bot, message.chat.id, cleanup_ids)

    topic_message = await message.answer("Введи тему обучения текстом.")

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        await service.remember_bot_message(assessment.id, topic_message.message_id)


@router.message(F.text == "Мой уровень")
async def my_level(message: Message) -> None:
    if message.from_user is None:
        return

    await safe_delete_user_message(message)

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        assessment = await service.get_latest_level(telegram_user_dto(message.from_user))

    if assessment is None:
        await message.answer("Пока нет завершённой оценки. Сначала нужно пройти оценку уровня.")
        return

    await message.answer(
        f"Твой последний уровень: {assessment.level_title or assessment.level}\n\n"
        f"Тема: {assessment.topic}\n"
        f"{assessment.description or ''}"
    )


@router.message(F.text.in_({"Список курсов", "Открыть обучение"}))
async def open_learning(message: Message) -> None:
    if message.from_user is None:
        return

    await safe_delete_user_message(message)

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        user_courses = await service.list_user_courses(telegram_user_dto(message.from_user))

    if not user_courses:
        await message.answer("Сначала нужно пройти оценку и подтвердить роадмап обучения.")
        return

    courses = CourseService().get_courses_from_user_courses(user_courses)
    await message.answer(
        format_courses_page(courses, page=0),
        reply_markup=courses_webapp_keyboard(courses, page=0),
    )