from aiogram.types import User as AiogramUser
from app.schemas.course import CourseDTO
from app.schemas.user import TelegramUserDTO
from app.db.models import Roadmap

COURSES_PAGE_SIZE = 5


def telegram_user_dto(user: AiogramUser) -> TelegramUserDTO:
    return TelegramUserDTO(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


def format_question(
    position: int,
    total: int,
    text: str,
    options: list | None = None,
) -> str:
    message = f"Вопрос {position} из {total}\n\n{text}"

    if options:
        letters = ["A", "B", "C", "D", "E", "F", "G", "H"]

        message += "\n\nВарианты ответа:"

        for index, option in enumerate(options):
            letter = letters[index] if index < len(letters) else str(index + 1)

            if isinstance(option, dict):
                option_text = option.get("label") or option.get("value") or ""
            else:
                option_text = str(option)

            message += f"\n\n{letter}. {option_text}"

    return message


def format_result(
    title: str,
    description: str,
    skills: list[str] | None,
    missing_skills: list[str] | None,
) -> str:
    skills_text = "\n".join(f"— {item}" for item in (skills or []))
    missing_text = "\n".join(f"— {item}" for item in (missing_skills or []))
    return (
        "Я определил твой уровень:\n\n"
        f"Уровень: {title}\n\n"
        "Описание:\n"
        f"{description}\n\n"
        "Навыки:\n"
        f"{skills_text}\n\n"
        "Что стоит подтянуть:\n"
        f"{missing_text}\n\n"
        "Согласен с результатом?"
    )


def format_roadmap(roadmap: Roadmap) -> str:
    lines = [f"Я подготовил роадмап обучения:\n\n{roadmap.title}"]
    for index, item in enumerate(roadmap.items_json, start=1):
        lines.append(
            "\n".join(
                [
                    f"{index}. {item['title']}",
                    f"Зачем: {item['why']}",
                    f"Буст: {item['career_boost']}",
                ]
            )
        )
    lines.append("Подходит такой план обучения?")
    return "\n\n".join(lines)

def format_courses_page(courses: list[CourseDTO], page: int = 0) -> str:
    if not courses:
        return "У тебя пока нет курсов."

    total_pages = max(1, (len(courses) + COURSES_PAGE_SIZE - 1) // COURSES_PAGE_SIZE)

    page = max(0, min(page, total_pages - 1))

    return (
        "Выбери курс для обучения:\n\n"
        f"Страница {page + 1} из {total_pages}"
    )