from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from app.bot.handlers.cleanup import cleanup_bot_messages
from app.bot.handlers.persistent_menu import ensure_persistent_menu
from app.bot.handlers.utils import format_question, format_result, format_roadmap, telegram_user_dto, format_courses_page
from app.bot.keyboards.inline import (
    AnswerCallback,
    ConfirmAssessmentCallback,
    CoursesPageCallback,
    ManualLevelCallback,
    RoadmapConfirmCallback,
    RoadmapRejectReasonCallback,
    confirmation_keyboard,
    courses_webapp_keyboard,
    manual_level_keyboard,
    question_keyboard,
    roadmap_confirmation_keyboard,
    roadmap_rejection_reasons_keyboard,
)
from app.db.database import async_session_factory
from app.db.models import AssessmentStatus
from app.services.assessment_service import AssessmentService
from app.services.course_service import CourseService
from app.services.neural_api import get_neural_api_service

router = Router()
MENU_COMMANDS = {
    "Пройти оценку",
    "Пройти новую оценку",
    "Мой уровень",
    "Открыть обучение",
    "Список курсов",
}


async def remember_message(assessment_id: int, message: Message) -> None:
    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        await service.remember_bot_message(assessment_id, message.message_id)


async def remember_roadmap_message(roadmap_id: int, message: Message) -> None:
    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        await service.remember_bot_message_for_roadmap(roadmap_id, message.message_id)


async def safe_callback_answer(callback: CallbackQuery, text: str | None = None, show_alert: bool = False) -> None:
    try:
        await callback.answer(text=text, show_alert=show_alert)
    except TelegramBadRequest:
        pass


async def show_loading(message: Message, text: str) -> Message:
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    return await message.answer(text)


async def safe_delete_message(message: Message | None) -> None:
    if message is None:
        return
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


@router.message(F.text & ~F.text.in_(MENU_COMMANDS))
async def topic_or_unexpected_text(message: Message) -> None:
    if message.from_user is None or message.text is None:
        return

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        user = await service.get_or_create_user(telegram_user_dto(message.from_user))
        assessment = await service.get_active_assessment(user)
        cleanup_ids: list[int] = []

        if assessment is None:
            await session.commit()
            await message.answer("Отправь /start, чтобы начать оценку.")
            return

        if assessment.status == AssessmentStatus.WAITING_TOPIC:
            try:
                cleanup_ids = await service.pop_bot_messages(assessment.id)
                topic_result = await service.handle_topic(telegram_user_dto(message.from_user), message.text)
            except Exception as e:
                print(e)
                await message.answer("Не получилось получить вопросы. Попробуй позже.")
                return

            if topic_result.first_question is None:
                await message.answer("Отправь /start, чтобы начать оценку заново.")
                return

            await cleanup_bot_messages(message.bot, message.chat.id, cleanup_ids)
            try:
                await message.delete()
            except TelegramBadRequest:
                pass
            question_message = await message.answer(
                format_question(
                    1,
                    topic_result.total_questions,
                    topic_result.first_question.question_text,
                    topic_result.first_question.options_json,
                ),
                reply_markup=question_keyboard(
                    topic_result.first_question.assessment_id,
                    topic_result.first_question,
                ),
            )
            await remember_message(topic_result.first_question.assessment_id, question_message)
            return

        await session.commit()

    if assessment.status == AssessmentStatus.IN_PROGRESS:
        await message.answer("Пожалуйста, выбери один из вариантов ответа кнопкой ниже.")
    elif assessment.status == AssessmentStatus.WAITING_CONFIRMATION:
        await message.answer("Пожалуйста, подтверди результат кнопкой ниже.")
    elif assessment.status == AssessmentStatus.REJECTED:
        await message.answer("Пожалуйста, выбери подходящий уровень кнопкой ниже.")
    else:
        await message.answer("Отправь /start, чтобы начать оценку.")


@router.callback_query(AnswerCallback.filter())
async def answer_question(callback: CallbackQuery, callback_data: AnswerCallback) -> None:
    await safe_callback_answer(callback)

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        try:
            result = await service.save_answer(
                telegram_user_id=callback.from_user.id,
                assessment_id=callback_data.assessment_id,
                question_id=callback_data.question_id,
                option_index=callback_data.option_index,
            )
        except Exception:
            await callback.message.answer("Не получилось обработать ответы. Попробуй позже.")
            return

    if result.already_processed:
        await callback.message.answer("Этот вопрос уже обработан.")
        return

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        cleanup_ids = await service.pop_bot_messages(callback_data.assessment_id)

    await cleanup_bot_messages(
        callback.bot,
        callback.message.chat.id,
        cleanup_ids or [callback.message.message_id],
        current_message=callback.message,
        transition_text="Ответ принят",
    )

    if result.next_question and result.assessment:
        next_message = await callback.message.answer(
            format_question(
                result.next_question.question_order + 1,
                result.total_questions,
                result.next_question.question_text,
                result.next_question.options_json,
            ),
            reply_markup=question_keyboard(result.assessment.id, result.next_question),
        )
        await remember_message(result.assessment.id, next_message)
        return

    if result.assessment_result and result.assessment:
        result_message = await callback.message.answer(
            format_result(
                result.assessment_result.title,
                result.assessment_result.description,
                result.assessment_result.skills,
                result.assessment_result.missing_skills,
            ),
            reply_markup=confirmation_keyboard(result.assessment.id),
        )
        await remember_message(result.assessment.id, result_message)
        return

    await callback.message.answer("Этот вопрос уже обработан.")


@router.callback_query(ConfirmAssessmentCallback.filter())
async def confirm_assessment(callback: CallbackQuery, callback_data: ConfirmAssessmentCallback) -> None:
    await safe_callback_answer(callback)

    loading_message = None
    if callback_data.accepted and callback.message is not None:
        loading_message = await show_loading(
            callback.message,
            "Готовлю роадмап. Это может занять несколько секунд...",
        )

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        assessment = await service.confirm_result(
            telegram_user_id=callback.from_user.id,
            assessment_id=callback_data.assessment_id,
            accepted=callback_data.accepted,
        )
        roadmap = None
        if assessment is not None and callback_data.accepted:
            try:
                roadmap = await service.generate_roadmap_for_assessment(callback.from_user.id, assessment)
            except Exception:
                roadmap = None
        cleanup_ids = await service.pop_bot_messages(callback_data.assessment_id)

    await safe_delete_message(loading_message)

    if assessment is None:
        await callback.message.answer("Этот результат уже обработан.")
        return

    if callback_data.accepted:
        await cleanup_bot_messages(
            callback.bot,
            callback.message.chat.id,
            cleanup_ids or [callback.message.message_id],
            current_message=callback.message,
            transition_text="Уровень сохранён",
        )
        if roadmap is None:
            error_message = await callback.message.answer(
                "Уровень сохранён, но не получилось получить роадмап от нейронки. Попробуй позже.",
            )
            await remember_message(assessment.id, error_message)
            await ensure_persistent_menu(
                callback.bot,
                callback.message.chat.id,
                callback.from_user,
                refresh_reply_keyboard=True,
            )
            return
        roadmap_message = await callback.message.answer(
            format_roadmap(roadmap),
            reply_markup=roadmap_confirmation_keyboard(roadmap.id),
        )
        await remember_roadmap_message(roadmap.id, roadmap_message)
    else:
        await cleanup_bot_messages(
            callback.bot,
            callback.message.chat.id,
            cleanup_ids or [callback.message.message_id],
            current_message=callback.message,
            transition_text="Понял",
        )
        manual_message = await callback.message.answer(
            "Хорошо. Какой уровень тебе кажется более подходящим?",
            reply_markup=manual_level_keyboard(assessment.id),
        )
        await remember_message(assessment.id, manual_message)


@router.callback_query(ManualLevelCallback.filter())
async def select_manual_level(callback: CallbackQuery, callback_data: ManualLevelCallback) -> None:
    await safe_callback_answer(callback)

    loading_message = None
    if callback.message is not None:
        loading_message = await show_loading(
            callback.message,
            "Готовлю роадмап под выбранный уровень...",
        )

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        assessment = await service.select_manual_level(
            telegram_user_id=callback.from_user.id,
            assessment_id=callback_data.assessment_id,
            level=callback_data.level,
        )
        roadmap = None
        if assessment is not None:
            try:
                roadmap = await service.generate_roadmap_for_assessment(callback.from_user.id, assessment)
            except Exception:
                roadmap = None
        cleanup_ids = await service.pop_bot_messages(callback_data.assessment_id)

    await safe_delete_message(loading_message)

    if assessment is None:
        await callback.message.answer("Этот выбор уже обработан.")
        return

    await cleanup_bot_messages(
        callback.bot,
        callback.message.chat.id,
        cleanup_ids or [callback.message.message_id],
        current_message=callback.message,
        transition_text="Уровень сохранён",
    )
    if roadmap is None:
        error_message = await callback.message.answer(
            "Уровень сохранён, но не получилось получить роадмап от нейронки. Попробуй позже.",
        )
        await remember_message(assessment.id, error_message)
        await ensure_persistent_menu(
            callback.bot,
            callback.message.chat.id,
            callback.from_user,
            refresh_reply_keyboard=True,
        )
        return
    roadmap_message = await callback.message.answer(
        format_roadmap(roadmap),
        reply_markup=roadmap_confirmation_keyboard(roadmap.id),
    )
    await remember_roadmap_message(roadmap.id, roadmap_message)


@router.callback_query(RoadmapConfirmCallback.filter())
async def confirm_roadmap(callback: CallbackQuery, callback_data: RoadmapConfirmCallback) -> None:
    await safe_callback_answer(callback)

    if callback.from_user is None or callback.message is None:
        return

    if not callback_data.accepted:
        async with async_session_factory() as session:
            service = AssessmentService(session, get_neural_api_service())
            cleanup_ids = await service.pop_bot_messages_for_roadmap(callback_data.roadmap_id)

        await cleanup_bot_messages(
            callback.bot,
            callback.message.chat.id,
            cleanup_ids or [callback.message.message_id],
            current_message=callback.message,
            transition_text="Понял",
        )

        reason_message = await callback.message.answer(
            "Что именно не подходит?",
            reply_markup=roadmap_rejection_reasons_keyboard(callback_data.roadmap_id),
        )

        await remember_roadmap_message(callback_data.roadmap_id, reason_message)
        return

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())

        cleanup_ids = await service.pop_bot_messages_for_roadmap(callback_data.roadmap_id)

        loading_message = await show_loading(
            callback.message,
            "Сохраняю роадмап и добавляю курс...",
        )

        roadmap = await service.accept_roadmap(
            telegram_user_dto(callback.from_user),
            callback_data.roadmap_id,
        )

        courses = await service.list_user_courses(
            telegram_user_dto(callback.from_user),
        )

    await safe_delete_message(loading_message)

    if roadmap is None:
        await callback.message.answer("Этот роадмап уже недоступен.")
        return

    course_buttons = CourseService().get_courses_from_user_courses(courses)

    await cleanup_bot_messages(
        callback.bot,
        callback.message.chat.id,
        cleanup_ids or [callback.message.message_id],
        current_message=callback.message,
        transition_text="Роадмап сохранён",
    )

    courses_message = await callback.message.answer(
        "Отлично, роадмап сохранён и добавлен в твои курсы.\n\n"
        + format_courses_page(course_buttons, page=0),
        reply_markup=courses_webapp_keyboard(course_buttons, page=0),
    )

    await ensure_persistent_menu(
        callback.bot,
        callback.message.chat.id,
        callback.from_user,
        refresh_reply_keyboard=True,
    )

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        await service.remember_bot_message_for_roadmap(
            callback_data.roadmap_id,
            courses_message.message_id,
        )


@router.callback_query(CoursesPageCallback.filter())
async def courses_page(
    callback: CallbackQuery,
    callback_data: CoursesPageCallback,
) -> None:
    await safe_callback_answer(callback)

    if callback.from_user is None or callback.message is None:
        return

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        user_courses = await service.list_user_courses(
            telegram_user_dto(callback.from_user)
        )

    courses = CourseService().get_courses_from_user_courses(user_courses)

    await callback.message.edit_text(
        format_courses_page(courses, page=callback_data.page),
        reply_markup=courses_webapp_keyboard(courses, page=callback_data.page),
    )


@router.callback_query(RoadmapRejectReasonCallback.filter())
async def reject_roadmap_reason(callback: CallbackQuery, callback_data: RoadmapRejectReasonCallback) -> None:
    await safe_callback_answer(callback)

    if callback.from_user is None:
        return

    loading_message = None
    if callback.message is not None:
        loading_message = await show_loading(
            callback.message,
            "Учитываю причину отказа и подбираю новый роадмап...",
        )

    async with async_session_factory() as session:
        service = AssessmentService(session, get_neural_api_service())
        cleanup_ids = await service.pop_bot_messages_for_roadmap(callback_data.roadmap_id)
        try:
            roadmap = await service.reject_and_regenerate_roadmap(
                telegram_user_id=callback.from_user.id,
                roadmap_id=callback_data.roadmap_id,
                reason=callback_data.reason,
            )
        except Exception:
            roadmap = None

    await safe_delete_message(loading_message)

    if roadmap is None:
        await callback.message.answer("Не получилось получить новый роадмап от нейронки. Попробуй позже.")
        return

    await cleanup_bot_messages(
        callback.bot,
        callback.message.chat.id,
        cleanup_ids or [callback.message.message_id],
        current_message=callback.message,
        transition_text="Подбираю новый роадмап",
    )
    roadmap_message = await callback.message.answer(
        format_roadmap(roadmap),
        reply_markup=roadmap_confirmation_keyboard(roadmap.id),
    )
    await remember_roadmap_message(roadmap.id, roadmap_message)
