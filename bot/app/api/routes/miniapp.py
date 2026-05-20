from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.db.database import async_session_factory
from app.db.models import Assessment, Roadmap, User
from app.services.telegram_webapp_auth import validate_telegram_init_data

router = APIRouter(prefix="/miniapp", tags=["miniapp"])


@router.get("/me")
async def miniapp_me(
    x_telegram_init_data: str = Header(alias="X-Telegram-Init-Data"),
) -> dict:
    telegram_user = validate_telegram_init_data(
        init_data=x_telegram_init_data,
        bot_token=settings.bot_token,
    )

    return {
        "ok": True,
        "user": {
            "id": telegram_user.get("id"),
            "username": telegram_user.get("username"),
            "first_name": telegram_user.get("first_name"),
            "last_name": telegram_user.get("last_name"),
        },
    }


@router.get("/roadmaps/{roadmap_id}")
async def miniapp_roadmap(
    roadmap_id: int,
    x_telegram_init_data: str = Header(alias="X-Telegram-Init-Data"),
) -> dict:
    telegram_user = validate_telegram_init_data(
        init_data=x_telegram_init_data,
        bot_token=settings.bot_token,
    )

    telegram_id = int(telegram_user["id"])

    async with async_session_factory() as session:
        query = (
            select(Roadmap)
            .join(Roadmap.assessment)
            .join(Assessment.user)
            .where(
                Roadmap.id == roadmap_id,
                User.telegram_id == telegram_id,
            )
        )

        result = await session.execute(query)
        roadmap = result.scalar_one_or_none()

    if roadmap is None:
        raise HTTPException(status_code=404, detail="roadmap_not_found_or_access_denied")

    return {
        "ok": True,
        "roadmap": {
            "id": roadmap.id,
            "topic": roadmap.topic,
            "level": roadmap.level,
            "title": roadmap.title,
            "items": roadmap.items_json,
            "courses": roadmap.courses_json,
        },
    }
