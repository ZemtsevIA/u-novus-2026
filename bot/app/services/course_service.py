from urllib.parse import urlencode

from app.core.config import settings
from app.db.models import Assessment, UserCourse
from app.schemas.course import CourseDTO


class CourseService:
    def get_courses_for_assessment(self, assessment: Assessment) -> list[CourseDTO]:
        topic = assessment.topic or "Обучение"
        level = assessment.level or "beginner"

        course_specs = [
            ("start", f"{topic}: стартовый модуль"),
            ("practice", f"{topic}: практика"),
            ("project", f"{topic}: учебный проект"),
        ]

        return [
            CourseDTO(
                id=f"{level}-{slug}",
                title=title,
                url=self._course_url(course_id=f"{level}-{slug}", topic=topic, level=level),
            )
            for slug, title in course_specs
        ]

    def _course_url(self, course_id: str, topic: str, level: str) -> str:
        separator = "&" if "?" in settings.mini_app_url else "?"
        query = urlencode(
            {
                "course_id": course_id,
                "topic": topic,
                "level": level,
            }
        )
        return f"{settings.mini_app_url}{separator}{query}"

    def get_courses_from_user_courses(self, user_courses: list[UserCourse]) -> list[CourseDTO]:
        return [
            CourseDTO(
                id=str(course.roadmap_id),
                title=course.title,
                url=self._roadmap_url(course.roadmap),
            )
            for course in user_courses
        ]

    def _roadmap_url(self, roadmap) -> str:
        separator = "&" if "?" in settings.mini_app_url else "?"
        query = urlencode(
            {
                "roadmap_id": roadmap.id,
                "topic": roadmap.topic,
                "level": roadmap.level,
                "title": roadmap.title,
            }
        )
        return f"{settings.mini_app_url}{separator}{query}"
