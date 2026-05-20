from pydantic import BaseModel


class TelegramUserDTO(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None

