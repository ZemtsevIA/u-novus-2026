from abc import ABC, abstractmethod
import asyncio
import logging
from pathlib import Path

import httpx
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.schemas.neural import AnswerDTO, QuestionDTO, SkillAssessmentDTO
from app.schemas.roadmap import NeuralRoadmapResponseDTO, RoadmapCourseDTO, RoadmapDTO, RoadmapItemDTO


ROADMAP_REJECTION_REASON_TITLES = {
    "too_hard": "слишком сложно",
    "too_easy": "слишком просто",
    "wrong_topic": "не та тема",
    "wrong_format": "не тот формат",
}

logger = logging.getLogger(__name__)


class NeuralApiService(ABC):
    @abstractmethod
    async def generate_questions(self, topic: str) -> list[QuestionDTO]:
        raise NotImplementedError

    @abstractmethod
    async def analyze_answers(
        self,
        telegram_user_id: int,
        topic: str,
        answers: list[AnswerDTO],
    ) -> SkillAssessmentDTO:
        raise NotImplementedError

    @abstractmethod
    async def send_user_confirmation(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        accepted: bool,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def generate_roadmap(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        preferences: str | None = None,
        rejection_reason: str | None = None,
    ) -> RoadmapDTO:
        raise NotImplementedError

    @abstractmethod
    async def correct_roadmap(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        current_roadmap: dict,
        courses: list[dict],
        feedback: str,
    ) -> RoadmapDTO:
        raise NotImplementedError

    @abstractmethod
    async def send_roadmap_feedback(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        roadmap_id: int,
        roadmap_title: str,
        roadmap_items: list[dict],
        accepted: bool,
        rejection_reason: str | None = None,
    ) -> None:
        raise NotImplementedError


class MockNeuralApiService(NeuralApiService):
    async def generate_questions(self, topic: str) -> list[QuestionDTO]:
        return [
            QuestionDTO(text="Есть ли у вас опыт программирования?", options=["Да", "Нет", "Немного"]),
            QuestionDTO(text="Знаете ли вы переменные, циклы и функции?", options=["Да", "Нет", "Частично"]),
            QuestionDTO(text="Работали ли вы с ООП?", options=["Да", "Нет", "Частично"]),
            QuestionDTO(text="Писали ли вы проекты на Python?", options=["Да", "Нет", "Учебные"]),
            QuestionDTO(text="Работали ли вы с backend-фреймворками?", options=["Да", "Нет", "Немного"]),
        ]

    async def analyze_answers(
        self,
        telegram_user_id: int,
        topic: str,
        answers: list[AnswerDTO],
    ) -> SkillAssessmentDTO:
        positive = sum(1 for item in answers if item.answer.lower() in {"да", "учебные"})
        partial = sum(1 for item in answers if item.answer.lower() in {"немного", "частично"})

        if positive >= 4:
            level = "experienced"
            title = "Опытный"
            description = "У пользователя уже есть уверенный практический опыт и понимание ключевых частей темы."
            skills = ["Практическая работа с темой", "Самостоятельное решение задач", "Понимание основных инструментов"]
            missing = ["Углубление архитектурных подходов", "Систематизация знаний"]
        elif positive + partial >= 3:
            level = "middle"
            title = "Средний"
            description = "У пользователя есть базовая и частично практическая подготовка, которую можно развивать дальше."
            skills = ["Базовые понятия программирования", "Начальная практика", "Понимание отдельных инструментов"]
            missing = ["ООП", "Backend-разработка", "Работа с базами данных"]
        else:
            level = "beginner"
            title = "Начинающий"
            description = "У пользователя есть базовое понимание темы, но не хватает практического опыта."
            skills = ["Базовые понятия программирования", "Начальное понимание Python"]
            missing = ["ООП", "Backend-разработка", "Работа с базами данных"]

        return SkillAssessmentDTO(
            level=level,
            title=title,
            description=description,
            skills=skills,
            missing_skills=missing,
        )

    async def send_user_confirmation(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        accepted: bool,
    ) -> None:
        return None

    async def generate_roadmap(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        preferences: str | None = None,
        rejection_reason: str | None = None,
    ) -> RoadmapDTO:
        response_path = Path("response_example.json")
        if response_path.exists():
            response = NeuralRoadmapResponseDTO.model_validate_json(response_path.read_text(encoding="utf-8"))
            response.roadmap.courses = response.courses
            if rejection_reason:
                reason_title = ROADMAP_REJECTION_REASON_TITLES.get(rejection_reason, rejection_reason)
                response.roadmap.summary = f"{response.roadmap.summary}\n\nОбновлено с учётом причины отказа: {reason_title}."
            return response.roadmap

        return RoadmapDTO(
            summary=f"Роадмап обучения: {topic}",
            items=[
                RoadmapItemDTO(
                    step=1,
                    title="Разобраться с базой",
                    why=f"Это даст фундамент для уверенного движения в теме «{topic}».",
                    career_boost="Собери короткий конспект и реши 5 простых задач.",
                ),
                RoadmapItemDTO(
                    step=2,
                    title="Закрепить практикой",
                    why="Практика быстро показывает пробелы и переводит знания из теории в навык.",
                    career_boost="Сделай небольшой учебный проект с понятным результатом.",
                ),
            ],
        )

    async def correct_roadmap(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        current_roadmap: dict,
        courses: list[dict],
        feedback: str,
    ) -> RoadmapDTO:
        return await self.generate_roadmap(
            telegram_user_id=telegram_user_id,
            topic=topic,
            level=level,
            preferences=None,
            rejection_reason=feedback,
        )

    async def send_roadmap_feedback(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        roadmap_id: int,
        roadmap_title: str,
        roadmap_items: list[dict],
        accepted: bool,
        rejection_reason: str | None = None,
    ) -> None:
        return None


class HttpNeuralApiService(NeuralApiService):
    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.fallback = MockNeuralApiService()

    @staticmethod
    def _roadmap_level(level: str) -> str:
        return {
            "beginner": "новичок",
            "middle": "средний",
            "experienced": "продвинутый",
        }.get(level, level)

    @staticmethod
    def _internal_level(level: str) -> str:
        normalized = level.strip().lower()
        if normalized in {"beginner", "новичок", "начинающий"}:
            return "beginner"
        if normalized in {"middle", "средний"}:
            return "middle"
        if normalized in {"experienced", "продвинутый", "опытный"}:
            return "experienced"
        return "beginner"

    @staticmethod
    def _level_title(level: str) -> str:
        return {
            "beginner": "Начинающий",
            "middle": "Средний",
            "experienced": "Опытный",
        }.get(level, "Начинающий")

    def _client(self, timeout: int = 30) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.config.neural_api_base_url,
            timeout=httpx.Timeout(timeout, connect=20),
            verify=self.config.neural_api_ssl_verify,
        )

    async def _post_json(self, path: str, payload: dict, timeout: int = 60) -> dict:
        last_error: Exception | None = None

        for attempt in range(1, 3):
            try:
                async with self._client(timeout=timeout) as client:
                    response = await client.post(
                        path,
                        json=payload,
                        headers=self._headers(),
                    )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as error:
                logger.warning(
                    "Neural API request failed: path=%s status=%s body=%s request=%s",
                    path,
                    error.response.status_code,
                    error.response.text[:1000],
                    payload,
                )
                raise
            except httpx.HTTPError as error:
                last_error = error
                logger.warning(
                    "Neural API request error: path=%s attempt=%s error=%s",
                    path,
                    attempt,
                    error,
                )
                if attempt == 1:
                    await asyncio.sleep(1)

        assert last_error is not None
        raise last_error

    @staticmethod
    def _parse_roadmap_payload(payload: dict, fallback_courses: list[dict] | None = None) -> RoadmapDTO:
        if "roadmap" in payload:
            parsed = NeuralRoadmapResponseDTO.model_validate(payload)
            parsed.roadmap.courses = parsed.courses
            return parsed.roadmap

        roadmap = RoadmapDTO.model_validate(payload)
        if not roadmap.courses and fallback_courses:
            roadmap.courses = [RoadmapCourseDTO.model_validate(course) for course in fallback_courses]
        return roadmap

    @staticmethod
    def _parse_survey_questions(payload: dict) -> list[QuestionDTO]:
        questions: list[QuestionDTO] = []
        for item in payload.get("questions", []):
            options = []
            for option in item.get("options", []):
                if isinstance(option, dict):
                    options.append(
                        {
                            "value": str(option.get("value") or option.get("label") or ""),
                            "label": str(option.get("label") or option.get("value") or ""),
                        }
                    )
                else:
                    options.append({"value": str(option), "label": str(option)})

            options = [option for option in options if option["value"] and option["label"]]
            if not options:
                continue

            questions.append(
                QuestionDTO(
                    id=str(item.get("id") or item.get("question_id") or item.get("order") or ""),
                    text=str(item.get("text") or item.get("question") or ""),
                    options=options,
                )
            )

        return [question for question in questions if question.text]

    @classmethod
    def _parse_survey_profile(cls, payload: dict) -> SkillAssessmentDTO:
        profile = payload.get("profile") or {}
        search_params = payload.get("search_params") or {}
        level = cls._internal_level(str(profile.get("level") or search_params.get("level") or ""))
        title = cls._level_title(level)

        domain = profile.get("domain") or "не указано"
        time_per_week = profile.get("time_per_week") or "не указано"
        format_pref = profile.get("format_pref") or "не указано"
        career_goal = profile.get("career_goal") or "не указано"
        preferences = search_params.get("preferences") or ""

        description = (
            f"Цель: {profile.get('goal') or search_params.get('topic') or 'не указано'}.\n"
            f"Направление: {domain}.\n"
            f"Темп: {time_per_week} в неделю.\n"
            f"Предпочтительный формат: {format_pref}.\n"
            f"Карьерная цель: {career_goal}."
        )

        skills = [
            f"Текущий уровень: {title}",
            f"Выбранное направление: {domain}",
            f"Удобный формат: {format_pref}",
        ]
        missing_skills = [
            "Практика по шагам роадмапа",
            "Закрепление материала проектами",
        ]
        if preferences:
            missing_skills.append(f"Учесть при обучении: {preferences}")

        return SkillAssessmentDTO(
            level=level,
            title=title,
            description=description,
            skills=skills,
            missing_skills=missing_skills,
            profile=profile,
            search_params=search_params,
        )

    async def generate_questions(self, topic: str) -> list[QuestionDTO]:
        if not self.config.neural_survey_api_enabled:
            return await self.fallback.generate_questions(topic)

        try:
            async with self._client(timeout=15) as client:
                response = await client.post(
                    "/api/survey/questions",
                    json={
                        "topic": topic,
                        "use_llm": self.config.neural_survey_use_llm,
                    },
                    headers=self._headers(),
                )
                response.raise_for_status()
            questions = self._parse_survey_questions(response.json())
            return questions or await self.fallback.generate_questions(topic)
        except httpx.HTTPStatusError as error:
            if error.response.status_code != 404:
                logger.warning(
                    "Neural API generate_questions failed: status=%s body=%s",
                    error.response.status_code,
                    error.response.text[:500],
                )
                raise
            return await self.fallback.generate_questions(topic)
        except (httpx.HTTPError, KeyError, ValidationError) as error:
            logger.warning("Neural API generate_questions fallback: %s", error)
            return await self.fallback.generate_questions(topic)

    async def analyze_answers(
        self,
        telegram_user_id: int,
        topic: str,
        answers: list[AnswerDTO],
    ) -> SkillAssessmentDTO:
        if self.config.neural_survey_api_enabled:
            survey_answers = {
                item.question_id: item.value or item.answer
                for item in answers
                if item.question_id
            }
            if survey_answers:
                try:
                    response_payload = await self._post_json(
                        "/api/survey/submit",
                        {
                            "topic": topic,
                            "answers": survey_answers,
                            "use_llm": self.config.neural_survey_use_llm,
                        },
                        timeout=30,
                    )
                    return self._parse_survey_profile(response_payload)
                except (httpx.HTTPError, ValidationError, ValueError) as error:
                    logger.warning("Neural API survey_submit fallback: %s", error)

        if not self.config.neural_assessment_api_enabled:
            return await self.fallback.analyze_answers(telegram_user_id, topic, answers)

        try:
            async with self._client(timeout=30) as client:
                response = await client.post(
                    "/analyze_answers",
                    json={
                        "telegram_user_id": telegram_user_id,
                        "topic": topic,
                        "answers": [item.model_dump() for item in answers],
                    },
                    headers=self._headers(),
                )
                response.raise_for_status()
            return SkillAssessmentDTO.model_validate(response.json())
        except httpx.HTTPStatusError as error:
            if error.response.status_code != 404:
                logger.warning(
                    "Neural API analyze_answers failed: status=%s body=%s",
                    error.response.status_code,
                    error.response.text[:500],
                )
                raise
            return await self.fallback.analyze_answers(telegram_user_id, topic, answers)
        except (httpx.HTTPError, ValidationError) as error:
            logger.warning("Neural API analyze_answers fallback: %s", error)
            return await self.fallback.analyze_answers(telegram_user_id, topic, answers)

    async def send_user_confirmation(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        accepted: bool,
    ) -> None:
        if not self.config.neural_assessment_api_enabled:
            return None

        try:
            async with self._client(timeout=15) as client:
                response = await client.post(
                    "/confirm_assessment",
                    json={
                        "telegram_user_id": telegram_user_id,
                        "topic": topic,
                        "level": level,
                        "accepted": accepted,
                    },
                    headers=self._headers(),
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as error:
            if error.response.status_code != 404:
                logger.warning(
                    "Neural API confirm_assessment failed: status=%s body=%s",
                    error.response.status_code,
                    error.response.text[:500],
                )
                raise
        except httpx.HTTPError as error:
            logger.warning("Neural API confirm_assessment skipped: %s", error)
            return None

    async def generate_roadmap(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        preferences: str | None = None,
        rejection_reason: str | None = None,
    ) -> RoadmapDTO:
        payload = {
            "topic": topic,
            "preferences": preferences or f"Пользователь хочет изучить: {topic}",
            "level": self._roadmap_level(level),
            "limit": 40,
            "refine_with_llm": True,
        }
        if rejection_reason:
            payload["preferences"] = f"{payload['preferences']}. Учесть предыдущий отказ: {rejection_reason}"

        try:
            response_payload = await self._post_json("/api/roadmap/remote-rag", payload, timeout=90)
            return self._parse_roadmap_payload(response_payload)
        except (ValidationError, ValueError) as error:
            logger.warning("Neural API generate_roadmap parse failed: %s", error)
            raise

    async def correct_roadmap(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        current_roadmap: dict,
        courses: list[dict],
        feedback: str,
    ) -> RoadmapDTO:
        payload = {
            "profile": {
                "goal": topic,
                "domain": "IT",
                "level": self._roadmap_level(level),
                "time_per_week": "5-7 часов",
                "format_pref": "любой",
                "career_goal": None,
            },
            "current_roadmap": current_roadmap,
            "feedback": feedback,
            "courses": courses,
        }

        try:
            response_payload = await self._post_json("/api/roadmap/correct", payload, timeout=90)
            return self._parse_roadmap_payload(response_payload, fallback_courses=courses)
        except (ValidationError, ValueError) as error:
            logger.warning("Neural API correct_roadmap parse failed: %s", error)
            raise

    async def send_roadmap_feedback(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        roadmap_id: int,
        roadmap_title: str,
        roadmap_items: list[dict],
        accepted: bool,
        rejection_reason: str | None = None,
    ) -> None:
        return None

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.config.neural_api_token}"}


def get_neural_api_service() -> NeuralApiService:
    if settings.use_mock_neural_api:
        return MockNeuralApiService()
    return HttpNeuralApiService(settings)
