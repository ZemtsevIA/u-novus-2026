from typing import Any

from pydantic import BaseModel, Field, field_validator


class QuestionOptionDTO(BaseModel):
    value: str
    label: str

    @field_validator("value", "label", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> str:
        return str(value)


class QuestionDTO(BaseModel):
    id: str | None = None
    text: str
    options: list[QuestionOptionDTO]

    @field_validator("options", mode="before")
    @classmethod
    def normalize_options(cls, value: Any) -> Any:
        if not isinstance(value, list):
            return value
        normalized = []
        for option in value:
            if isinstance(option, dict):
                option_value = option.get("value") or option.get("label") or ""
                option_label = option.get("label") or option.get("value") or ""
                normalized.append({"value": option_value, "label": option_label})
            else:
                normalized.append({"value": option, "label": option})
        return normalized


class AnswerDTO(BaseModel):
    question_id: str | None = None
    question: str
    answer: str
    value: str | None = None


class SkillAssessmentDTO(BaseModel):
    level: str = Field(pattern="^(beginner|middle|experienced)$")
    title: str
    description: str
    skills: list[str]
    missing_skills: list[str]
    profile: dict | None = None
    search_params: dict | None = None
