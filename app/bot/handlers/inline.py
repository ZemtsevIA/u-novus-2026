from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.schemas.course import CourseDTO


COURSES_PAGE_SIZE = 5


class CoursesPageCallback(CallbackData, prefix="courses_page"):
    page: int


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
                    web_app=WebAppInfo(url=course.url),
                )
            ]
        )

    nav_row: list[InlineKeyboardButton] = []

    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=CoursesPageCallback(page=page - 1).pack(),
            )
        )

    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️ Далее",
                callback_data=CoursesPageCallback(page=page + 1).pack(),
            )
        )

    if nav_row:
        keyboard.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)