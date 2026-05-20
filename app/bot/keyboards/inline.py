from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.config import settings
from app.db.models import AssessmentQuestion
from app.schemas.assessment import LEVEL_TITLES
from app.schemas.course import CourseDTO


class AnswerCallback(CallbackData, prefix="answer"):
    assessment_id: int
    question_id: int
    option_index: int


class ConfirmAssessmentCallback(CallbackData, prefix="confirm_assessment"):
    assessment_id: int
    accepted: bool


class ManualLevelCallback(CallbackData, prefix="manual_level"):
    assessment_id: int
    level: str


class RoadmapConfirmCallback(CallbackData, prefix="roadmap_confirm"):
    roadmap_id: int
    accepted: bool


class RoadmapRejectReasonCallback(CallbackData, prefix="roadmap_reject"):
    roadmap_id: int
    reason: str
    
class CoursesPageCallback(CallbackData, prefix="courses_page"):
    page: int


ROADMAP_REJECTION_REASONS = {
    "too_hard": "Слишком сложно",
    "too_easy": "Слишком просто",
    "wrong_topic": "Не та тема",
    "wrong_format": "Не тот формат",
}


def start_assessment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать оценку", callback_data="start_assessment")],
        ]
    )


def question_keyboard(assessment_id: int, question: AssessmentQuestion) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    letters = ["A", "B", "C", "D", "E", "F", "G", "H"]

    for index, option in enumerate(question.options_json):
        letter = letters[index] if index < len(letters) else str(index + 1)

        builder.button(
            text=f"Ответ {letter}",
            callback_data=AnswerCallback(
                assessment_id=assessment_id,
                question_id=question.id,
                option_index=index,
            ),
        )

    builder.adjust(2)
    return builder.as_markup()


def confirmation_keyboard(assessment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, согласен",
                    callback_data=ConfirmAssessmentCallback(assessment_id=assessment_id, accepted=True).pack(),
                ),
                InlineKeyboardButton(
                    text="Нет, не согласен",
                    callback_data=ConfirmAssessmentCallback(assessment_id=assessment_id, accepted=False).pack(),
                ),
            ]
        ]
    )


def manual_level_keyboard(assessment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for level, title in LEVEL_TITLES.items():
        builder.button(
            text=title,
            callback_data=ManualLevelCallback(assessment_id=assessment_id, level=level),
        )
    builder.adjust(3)
    return builder.as_markup()


def miniapp_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть обучение", web_app=WebAppInfo(url=settings.mini_app_url))]
        ]
    )


COURSES_PAGE_SIZE = 5


def short_button_text(text: str, limit: int = 45) -> str:
    if len(text) <= limit:
        return text
    return text[:limit - 3] + "..."


def courses_webapp_keyboard(
    courses: list[CourseDTO],
    page: int = 0,
) -> InlineKeyboardMarkup:
    total_pages = max(1, (len(courses) + COURSES_PAGE_SIZE - 1) // COURSES_PAGE_SIZE)

    page = max(0, min(page, total_pages - 1))

    start = page * COURSES_PAGE_SIZE
    end = start + COURSES_PAGE_SIZE
    page_courses = courses[start:end]

    keyboard: list[list[InlineKeyboardButton]] = []

    for course in page_courses:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=short_button_text(course.title),
                    web_app=WebAppInfo(url=f"{settings.mini_app_url}/course?course_id={course.id}"),
                )
            ]
        )

    navigation_buttons: list[InlineKeyboardButton] = []

    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=CoursesPageCallback(page=page - 1).pack(),
            )
        )

    if page < total_pages - 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="➡️ Далее",
                callback_data=CoursesPageCallback(page=page + 1).pack(),
            )
        )

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def roadmap_confirmation_keyboard(roadmap_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Согласен",
                    callback_data=RoadmapConfirmCallback(roadmap_id=roadmap_id, accepted=True).pack(),
                ),
                InlineKeyboardButton(
                    text="Не согласен",
                    callback_data=RoadmapConfirmCallback(roadmap_id=roadmap_id, accepted=False).pack(),
                ),
            ]
        ]
    )


def roadmap_rejection_reasons_keyboard(roadmap_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for reason, title in ROADMAP_REJECTION_REASONS.items():
        builder.button(
            text=title,
            callback_data=RoadmapRejectReasonCallback(roadmap_id=roadmap_id, reason=reason),
        )
    builder.adjust(2)
    return builder.as_markup()
