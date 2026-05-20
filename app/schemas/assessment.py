from pydantic import BaseModel


LEVEL_TITLES = {
    "beginner": "Начинающий",
    "middle": "Средний",
    "experienced": "Опытный",
}


class AssessmentResultView(BaseModel):
    level: str
    title: str
    description: str
    skills: list[str]
    missing_skills: list[str]

