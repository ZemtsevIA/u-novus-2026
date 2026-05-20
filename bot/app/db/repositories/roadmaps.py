from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Roadmap, RoadmapStatus, UserCourse
from app.schemas.roadmap import RoadmapDTO


class RoadmapRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        assessment_id: int,
        topic: str,
        level: str,
        roadmap: RoadmapDTO,
    ) -> Roadmap:
        entity = Roadmap(
            assessment_id=assessment_id,
            topic=topic,
            level=level,
            title=roadmap.title,
            items_json=[item.model_dump() for item in roadmap.items],
            courses_json=[course.model_dump() for course in roadmap.courses],
            status=RoadmapStatus.GENERATED,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, roadmap_id: int) -> Roadmap | None:
        result = await self.session.execute(
            select(Roadmap)
            .options(selectinload(Roadmap.assessment))
            .where(Roadmap.id == roadmap_id)
        )
        return result.scalar_one_or_none()

    async def accept(self, roadmap: Roadmap) -> None:
        roadmap.status = RoadmapStatus.ACCEPTED
        roadmap.rejection_reason = None
        await self.session.flush()

    async def reject(self, roadmap: Roadmap, reason: str) -> None:
        roadmap.status = RoadmapStatus.REJECTED
        roadmap.rejection_reason = reason
        await self.session.flush()

    async def add_user_course(self, user_id: int, roadmap: Roadmap) -> UserCourse:
        result = await self.session.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.roadmap_id == roadmap.id,
            )
        )
        course = result.scalar_one_or_none()
        if course is not None:
            return course

        course = UserCourse(user_id=user_id, roadmap_id=roadmap.id, title=roadmap.title)
        self.session.add(course)
        await self.session.flush()
        return course

    async def list_user_courses(self, user_id: int) -> list[UserCourse]:
        result = await self.session.execute(
            select(UserCourse)
            .options(selectinload(UserCourse.roadmap))
            .where(UserCourse.user_id == user_id)
            .order_by(UserCourse.created_at.desc(), UserCourse.id.desc())
        )
        return list(result.scalars().all())
