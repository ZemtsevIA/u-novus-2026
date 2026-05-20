from fastapi import APIRouter

from app.db.database import async_session_factory
from app.db.repositories.roadmaps import RoadmapRepository

router = APIRouter(prefix="/miniapp", tags=["miniapp"])


@router.get("/me")
async def miniapp_me() -> dict[str, str]:
    return {"status": "stub", "message": "Mini App auth will be added later"}


@router.get("/roadmaps/{roadmap_id}")
async def miniapp_roadmap(roadmap_id: int) -> dict:
    async with async_session_factory() as session:
        roadmap = await RoadmapRepository(session).get_by_id(roadmap_id)

    if roadmap is None:
        return {"ok": False, "error": "roadmap_not_found"}

    return {
        "ok": True,
        "roadmap": {
            "id": roadmap.id,
            "topic": roadmap.topic,
            "level": roadmap.level,
            "title": roadmap.title,
            "items": roadmap.items_json,
        },
    }
