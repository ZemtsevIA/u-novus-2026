from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard(has_courses: bool = False) -> ReplyKeyboardMarkup:
    if has_courses:
        keyboard = [
            [KeyboardButton(text="Список курсов")],
            [KeyboardButton(text="Пройти новую оценку")],
            [KeyboardButton(text="Мой уровень")],
        ]
    else:
        keyboard = [
            [KeyboardButton(text="Пройти оценку")],
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )
