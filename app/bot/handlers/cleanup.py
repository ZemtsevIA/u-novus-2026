import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def cleanup_bot_messages(
    bot: Bot,
    chat_id: int,
    message_ids: list[int],
    current_message: Message | None = None,
    transition_text: str = "Готово",
) -> None:
    unique_ids = list(dict.fromkeys(message_ids))

    if current_message and current_message.message_id in unique_ids:
        try:
            await current_message.edit_text(transition_text)
            await asyncio.sleep(0.25)
        except TelegramBadRequest:
            pass

    for message_id in unique_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except TelegramBadRequest:
            pass

