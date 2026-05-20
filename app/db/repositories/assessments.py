from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Assessment, AssessmentQuestion, AssessmentStatus
from app.schemas.neural import QuestionDTO


FINAL_STATUSES = {
    AssessmentStatus.ACCEPTED,
    AssessmentStatus.MANUALLY_SELECTED,
    AssessmentStatus.COMPLETED,
}

ACTIVE_STATUSES = {
    AssessmentStatus.CREATED,
    AssessmentStatus.WAITING_TOPIC,
    AssessmentStatus.QUESTIONS_GENERATED,
    AssessmentStatus.IN_PROGRESS,
    AssessmentStatus.WAITING_CONFIRMATION,
    AssessmentStatus.REJECTED,
}


class AssessmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: int, status: AssessmentStatus = AssessmentStatus.WAITING_TOPIC) -> Assessment:
        assessment = Assessment(user_id=user_id, status=status)
        self.session.add(assessment)
        await self.session.flush()
        return assessment

    async def get_by_id(self, assessment_id: int) -> Assessment | None:
        result = await self.session.execute(
            select(Assessment)
            .options(selectinload(Assessment.questions))
            .where(Assessment.id == assessment_id)
        )
        return result.scalar_one_or_none()

    async def get_active_for_user(self, user_id: int) -> Assessment | None:
        result = await self.session.execute(
            select(Assessment)
            .options(selectinload(Assessment.questions))
            .where(Assessment.user_id == user_id, Assessment.status.in_(ACTIVE_STATUSES))
            .order_by(desc(Assessment.created_at), desc(Assessment.id))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_completed_for_user(self, user_id: int) -> Assessment | None:
        result = await self.session.execute(
            select(Assessment)
            .where(
                Assessment.user_id == user_id,
                Assessment.miniapp_available.is_(True),
                Assessment.level.is_not(None),
            )
            .order_by(desc(Assessment.updated_at), desc(Assessment.id))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def set_topic(self, assessment: Assessment, topic: str) -> None:
        assessment.topic = topic
        assessment.status = AssessmentStatus.QUESTIONS_GENERATED
        await self.session.flush()

    async def add_questions(self, assessment: Assessment, questions: list[QuestionDTO]) -> list[AssessmentQuestion]:
        created = [
            AssessmentQuestion(
                assessment_id=assessment.id,
                question_order=index,
                external_question_id=question.id,
                question_text=question.text,
                options_json=[option.model_dump() for option in question.options],
            )
            for index, question in enumerate(questions)
        ]
        self.session.add_all(created)
        assessment.status = AssessmentStatus.IN_PROGRESS
        assessment.current_question_index = 0
        await self.session.flush()
        return created

    async def save_answer(self, question: AssessmentQuestion, answer: str, answer_value: str | None = None) -> None:
        question.answer_text = answer
        question.answer_value = answer_value or answer
        await self.session.flush()

    async def update_assessment(self, assessment: Assessment) -> None:
        self.session.add(assessment)
        await self.session.flush()
