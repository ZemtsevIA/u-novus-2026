from pydantic import BaseModel, Field


class QuestionDTO(BaseModel):
    text: str
    options: list[str]


class AnswerDTO(BaseModel):
    question: str
    answer: str


class SkillAssessmentDTO(BaseModel):
    level: str = Field(pattern="^(beginner|middle|experienced)$")
    title: str
    description: str
    skills: list[str]
    missing_skills: list[str]

