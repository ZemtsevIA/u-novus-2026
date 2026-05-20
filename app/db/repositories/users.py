from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas.user import TelegramUserDTO


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_or_create(self, data: TelegramUserDTO) -> User:
        user = await self.get_by_telegram_id(data.telegram_id)
        if user is None:
            user = User(**data.model_dump())
            self.session.add(user)
            await self.session.flush()
            return user

        user.username = data.username
        user.first_name = data.first_name
        user.last_name = data.last_name
        await self.session.flush()
        return user

    async def set_welcome_message_id(self, user: User, message_id: int) -> None:
        user.welcome_message_id = message_id
        await self.session.flush()
