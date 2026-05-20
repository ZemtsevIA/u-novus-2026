from abc import ABC, abstractmethod
from pathlib import Path

import httpx

from app.core.config import Settings, settings
from app.schemas.neural import AnswerDTO, QuestionDTO, SkillAssessmentDTO
from app.schemas.roadmap import NeuralRoadmapResponseDTO, RoadmapDTO, RoadmapItemDTO


ROADMAP_REJECTION_REASON_TITLES = {
    "too_hard": "слишком сложно",
    "too_easy": "слишком просто",
    "wrong_topic": "не та тема",
    "wrong_format": "не тот формат",
}


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
        rejection_reason: str | None = None,
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
        rejection_reason: str | None = None,
    ) -> RoadmapDTO:
        response_path = Path("response_example.json")
        if response_path.exists():
            response = NeuralRoadmapResponseDTO.model_validate_json(response_path.read_text(encoding="utf-8"))
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

    async def generate_questions(self, topic: str) -> list[QuestionDTO]:
        async with httpx.AsyncClient(base_url=self.config.neural_api_base_url, timeout=15) as client:
            response = await client.post(
                "/generate_questions",
                json={"topic": topic},
                headers=self._headers(),
            )
            response.raise_for_status()
        payload = response.json()
        return [QuestionDTO.model_validate(item) for item in payload["questions"]]

    async def analyze_answers(
        self,
        telegram_user_id: int,
        topic: str,
        answers: list[AnswerDTO],
    ) -> SkillAssessmentDTO:
        async with httpx.AsyncClient(base_url=self.config.neural_api_base_url, timeout=30) as client:
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

    async def send_user_confirmation(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        accepted: bool,
    ) -> None:
        async with httpx.AsyncClient(base_url=self.config.neural_api_base_url, timeout=15) as client:
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

    async def generate_roadmap(
        self,
        telegram_user_id: int,
        topic: str,
        level: str,
        rejection_reason: str | None = None,
    ) -> RoadmapDTO:
        payload = {
            "telegram_user_id": telegram_user_id,
            "topic": topic,
            "level": level,
        }
        if rejection_reason:
            payload["rejection_reason"] = rejection_reason

        async with httpx.AsyncClient(base_url=self.config.neural_api_base_url, timeout=30) as client:
            response = await client.post(
                "/generate_roadmap",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
        payload = response.json()
        if "roadmap" in payload:
            return NeuralRoadmapResponseDTO.model_validate(payload).roadmap
        return RoadmapDTO.model_validate(payload)

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
        payload = {
            "telegram_user_id": telegram_user_id,
            "topic": topic,
            "level": level,
            "roadmap": {
                "id": roadmap_id,
                "title": roadmap_title,
                "items": roadmap_items,
            },
            "accepted": accepted,
        }
        if rejection_reason:
            payload["rejection_reason"] = rejection_reason

        async with httpx.AsyncClient(base_url=self.config.neural_api_base_url, timeout=15) as client:
            response = await client.post(
                "/roadmap_feedback",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.config.neural_api_token}"}


def get_neural_api_service() -> NeuralApiService:
    if settings.use_mock_neural_api:
        return MockNeuralApiService()
    return HttpNeuralApiService(settings)
