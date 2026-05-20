from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Assessment, AssessmentQuestion, AssessmentStatus, Roadmap, User
from app.db.repositories.assessments import AssessmentRepository
from app.db.repositories.roadmaps import RoadmapRepository
from app.db.repositories.users import UserRepository
from app.schemas.assessment import LEVEL_TITLES
from app.schemas.neural import AnswerDTO, SkillAssessmentDTO
from app.schemas.user import TelegramUserDTO
from app.services.neural_api import NeuralApiService


@dataclass(slots=True)
class TopicResult:
    first_question: AssessmentQuestion | None = None
    total_questions: int = 0


@dataclass(slots=True)
class AnswerResult:
    already_processed: bool = False
    next_question: AssessmentQuestion | None = None
    assessment_result: SkillAssessmentDTO | None = None
    total_questions: int = 0
    assessment: Assessment | None = None


class AssessmentService:
    def __init__(self, session: AsyncSession, neural_api: NeuralApiService) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.assessments = AssessmentRepository(session)
        self.roadmaps = RoadmapRepository(session)
        self.neural_api = neural_api

    async def get_or_create_user(self, user_data: TelegramUserDTO) -> User:
        return await self.users.get_or_create(user_data)

    async def get_menu_user(self, user_data: TelegramUserDTO) -> User:
        user = await self.get_or_create_user(user_data)
        await self.session.commit()
        return user

    async def set_welcome_message_id(self, user: User, message_id: int) -> None:
        await self.users.set_welcome_message_id(user, message_id)
        await self.session.commit()

    async def user_has_completed_assessment(self, user: User) -> bool:
        return await self.assessments.get_latest_completed_for_user(user.id) is not None

    async def start_assessment(self, user_data: TelegramUserDTO) -> Assessment:
        user = await self.users.get_or_create(user_data)
        assessment = await self.assessments.create(user.id)
        await self.session.commit()
        return assessment

    async def remember_bot_message(self, assessment_id: int, message_id: int) -> None:
        assessment = await self.assessments.get_by_id(assessment_id)
        if assessment is None:
            await self.session.commit()
            return

        message_ids = list(assessment.bot_message_ids or [])
        if message_id not in message_ids:
            message_ids.append(message_id)
        assessment.bot_message_ids = message_ids
        await self.session.flush()
        await self.session.commit()

    async def pop_bot_messages(self, assessment_id: int) -> list[int]:
        assessment = await self.assessments.get_by_id(assessment_id)
        if assessment is None:
            await self.session.commit()
            return []

        message_ids = list(assessment.bot_message_ids or [])
        assessment.bot_message_ids = []
        await self.session.flush()
        await self.session.commit()
        return message_ids

    async def remember_bot_message_for_roadmap(self, roadmap_id: int, message_id: int) -> None:
        roadmap = await self.roadmaps.get_by_id(roadmap_id)
        if roadmap is None:
            await self.session.commit()
            return
        await self.remember_bot_message(roadmap.assessment_id, message_id)

    async def pop_bot_messages_for_roadmap(self, roadmap_id: int) -> list[int]:
        roadmap = await self.roadmaps.get_by_id(roadmap_id)
        if roadmap is None:
            await self.session.commit()
            return []
        return await self.pop_bot_messages(roadmap.assessment_id)

    async def handle_topic(self, user_data: TelegramUserDTO, topic: str) -> TopicResult:
        user = await self.users.get_or_create(user_data)
        assessment = await self.assessments.get_active_for_user(user.id)
        if assessment is None or assessment.status != AssessmentStatus.WAITING_TOPIC:
            await self.session.commit()
            return TopicResult()

        await self.assessments.set_topic(assessment, topic.strip())
        questions = await self.neural_api.generate_questions(topic.strip())
        created_questions = await self.assessments.add_questions(assessment, questions)
        total_questions = len(created_questions)
        await self.session.commit()
        return TopicResult(
            first_question=created_questions[0] if created_questions else None,
            total_questions=total_questions,
        )

    async def get_active_assessment(self, user: User) -> Assessment | None:
        return await self.assessments.get_active_for_user(user.id)

    async def save_answer(
        self,
        telegram_user_id: int,
        assessment_id: int,
        question_id: int,
        option_index: int,
    ) -> AnswerResult:
        assessment = await self.assessments.get_by_id(assessment_id)
        if assessment is None or assessment.status != AssessmentStatus.IN_PROGRESS:
            return AnswerResult(already_processed=True)

        questions = sorted(assessment.questions, key=lambda item: item.question_order)
        question = next((item for item in questions if item.id == question_id), None)
        if question is None or question.answer_text is not None:
            return AnswerResult(already_processed=True)

        if question.question_order != assessment.current_question_index:
            return AnswerResult(already_processed=True)

        try:
            option = question.options_json[option_index]
        except IndexError:
            return AnswerResult(already_processed=True)

        if isinstance(option, dict):
            answer = str(option.get("label") or option.get("value") or "")
            answer_value = str(option.get("value") or answer)
        else:
            answer = str(option)
            answer_value = answer

        await self.assessments.save_answer(question, answer, answer_value)
        assessment.current_question_index += 1

        if assessment.current_question_index < len(questions):
            await self.assessments.update_assessment(assessment)
            await self.session.commit()
            return AnswerResult(
                next_question=questions[assessment.current_question_index],
                total_questions=len(questions),
                assessment=assessment,
            )

        answers = [
            AnswerDTO(
                question_id=item.external_question_id,
                question=item.question_text,
                answer=item.answer_text or "",
                value=item.answer_value or item.answer_text or "",
            )
            for item in questions
        ]
        result = await self.neural_api.analyze_answers(
            telegram_user_id=telegram_user_id,
            topic=assessment.topic or "",
            answers=answers,
        )
        assessment.level = result.level
        assessment.level_title = result.title
        assessment.description = result.description
        assessment.skills = result.skills
        assessment.missing_skills = result.missing_skills
        assessment.profile_json = result.profile
        assessment.search_params_json = result.search_params
        assessment.status = AssessmentStatus.WAITING_CONFIRMATION
        await self.assessments.update_assessment(assessment)
        await self.session.commit()
        return AnswerResult(
            assessment_result=result,
            total_questions=len(questions),
            assessment=assessment,
        )

    async def confirm_result(self, telegram_user_id: int, assessment_id: int, accepted: bool) -> Assessment | None:
        assessment = await self.assessments.get_by_id(assessment_id)
        if assessment is None or assessment.status != AssessmentStatus.WAITING_CONFIRMATION:
            return None

        assessment.accepted = accepted
        if accepted:
            assessment.status = AssessmentStatus.ACCEPTED
            assessment.miniapp_available = False
            await self.neural_api.send_user_confirmation(
                telegram_user_id=telegram_user_id,
                topic=assessment.topic or "",
                level=assessment.level or "beginner",
                accepted=True,
            )
        else:
            assessment.status = AssessmentStatus.REJECTED
            await self.neural_api.send_user_confirmation(
                telegram_user_id=telegram_user_id,
                topic=assessment.topic or "",
                level=assessment.level or "beginner",
                accepted=False,
            )

        await self.assessments.update_assessment(assessment)
        await self.session.commit()
        return assessment

    async def generate_roadmap_for_assessment(
        self,
        telegram_user_id: int,
        assessment: Assessment,
        rejection_reason: str | None = None,
    ):
        roadmap_dto = await self.neural_api.generate_roadmap(
            telegram_user_id=telegram_user_id,
            topic=(assessment.search_params_json or {}).get("topic") or assessment.topic or "",
            level=(assessment.search_params_json or {}).get("level") or assessment.level or "beginner",
            preferences=(assessment.search_params_json or {}).get("preferences"),
            rejection_reason=rejection_reason,
        )
        roadmap = await self.roadmaps.create(
            assessment_id=assessment.id,
            topic=assessment.topic or "",
            level=assessment.level or "beginner",
            roadmap=roadmap_dto,
        )
        await self.session.commit()
        return roadmap

    async def select_manual_level(self, telegram_user_id: int, assessment_id: int, level: str) -> Assessment | None:
        if level not in LEVEL_TITLES:
            return None

        assessment = await self.assessments.get_by_id(assessment_id)
        if assessment is None or assessment.status != AssessmentStatus.REJECTED:
            return None

        assessment.level = level
        assessment.level_title = LEVEL_TITLES[level]
        assessment.description = "Уровень выбран пользователем вручную после оценки."
        assessment.accepted = False
        assessment.manual_level_selected = True
        assessment.miniapp_available = False
        assessment.status = AssessmentStatus.MANUALLY_SELECTED
        await self.neural_api.send_user_confirmation(
            telegram_user_id=telegram_user_id,
            topic=assessment.topic or "",
            level=level,
            accepted=False,
        )
        await self.assessments.update_assessment(assessment)
        await self.session.commit()
        return assessment

    async def accept_roadmap(self, user_data: TelegramUserDTO, roadmap_id: int):
        user = await self.users.get_or_create(user_data)
        roadmap = await self.roadmaps.get_by_id(roadmap_id)
        if roadmap is None:
            await self.session.commit()
            return None

        await self.neural_api.send_roadmap_feedback(
            telegram_user_id=user_data.telegram_id,
            topic=roadmap.topic,
            level=roadmap.level,
            roadmap_id=roadmap.id,
            roadmap_title=roadmap.title,
            roadmap_items=roadmap.items_json,
            accepted=True,
        )
        await self.roadmaps.accept(roadmap)
        await self.roadmaps.add_user_course(user.id, roadmap)
        roadmap.assessment.status = AssessmentStatus.COMPLETED
        roadmap.assessment.miniapp_available = True
        await self.session.flush()
        await self.session.commit()
        return roadmap

    async def reject_roadmap(self, roadmap_id: int, reason: str):
        roadmap = await self.roadmaps.get_by_id(roadmap_id)
        if roadmap is None:
            await self.session.commit()
            return None

        await self.roadmaps.reject(roadmap, reason)
        await self.session.commit()
        return roadmap

    async def reject_and_regenerate_roadmap(
        self,
        telegram_user_id: int,
        roadmap_id: int,
        reason: str,
    ):
        roadmap = await self.roadmaps.get_by_id(roadmap_id)
        if roadmap is None:
            await self.session.commit()
            return None

        assessment = roadmap.assessment
        await self.roadmaps.reject(roadmap, reason)
        await self.neural_api.send_roadmap_feedback(
            telegram_user_id=telegram_user_id,
            topic=roadmap.topic,
            level=roadmap.level,
            roadmap_id=roadmap.id,
            roadmap_title=roadmap.title,
            roadmap_items=roadmap.items_json,
            accepted=False,
            rejection_reason=reason,
        )
        current_roadmap = {
            "summary": roadmap.title,
            "steps": roadmap.items_json,
        }
        roadmap_dto = await self.neural_api.correct_roadmap(
            telegram_user_id=telegram_user_id,
            topic=assessment.topic or roadmap.topic,
            level=assessment.level or roadmap.level,
            current_roadmap=current_roadmap,
            courses=roadmap.courses_json or [],
            feedback=reason,
        )
        new_roadmap = await self.roadmaps.create(
            assessment_id=assessment.id,
            topic=assessment.topic or roadmap.topic,
            level=assessment.level or roadmap.level,
            roadmap=roadmap_dto,
        )
        await self.session.commit()
        return new_roadmap

    async def get_latest_level(self, user_data: TelegramUserDTO) -> Assessment | None:
        user = await self.users.get_or_create(user_data)
        assessment = await self.assessments.get_latest_completed_for_user(user.id)
        await self.session.commit()
        return assessment

    async def can_open_miniapp(self, user_data: TelegramUserDTO) -> bool:
        user = await self.users.get_or_create(user_data)
        assessment = await self.assessments.get_latest_completed_for_user(user.id)
        await self.session.commit()
        return assessment is not None

    async def get_latest_completed_assessment(self, user_data: TelegramUserDTO) -> Assessment | None:
        user = await self.users.get_or_create(user_data)
        assessment = await self.assessments.get_latest_completed_for_user(user.id)
        await self.session.commit()
        return assessment

    async def list_user_courses(self, user_data: TelegramUserDTO):
        user = await self.users.get_or_create(user_data)
        courses = await self.roadmaps.list_user_courses(user.id)
        await self.session.commit()
        return courses
    
    async def pop_user_roadmap_messages(self, user_id: int) -> list[int]:
        assessments = await self.session.scalars(
            select(Assessment).where(Assessment.user_id == user_id)
        )

        message_ids: list[int] = []

        for assessment in assessments:
            ids = list(assessment.bot_message_ids or [])
            if ids:
                message_ids.extend(ids)
                assessment.bot_message_ids = []

        await self.session.flush()
        await self.session.commit()

        return message_ids
