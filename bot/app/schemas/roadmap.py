from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator


class SearchRequestDTO(BaseModel):
    topic: str = ""
    preferences: str | None = None
    level: str | None = None
    limit: int | None = None


class RefinedSearchRequestDTO(BaseModel):
    topic: str = ""
    preferences: str | None = None
    level: str | None = None


class RoadmapCourseDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    platform: str | None = None
    level: str | None = None
    format: str | None = None
    description: str | None = None
    url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_course(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = dict(value)
        title = data.get("title") or data.get("name") or data.get("course_title") or "Курс"
        data["title"] = str(title)
        data["id"] = str(
            data.get("id")
            or data.get("course_id")
            or data.get("url")
            or data["title"]
        )
        return data


class RoadmapItemDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    step: int | None = None
    title: str
    course_id: str | None = None
    course_title: str | None = None
    course_url: str | None = None
    format: str | None = None
    duration_hours: int | None = None
    skills: list[str] = Field(default_factory=list)
    why: str = ""
    career_boost: str = Field(
        default="",
        validation_alias=AliasChoices("career_boost", "boost"),
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_item(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = dict(value)
        data["title"] = str(data.get("title") or data.get("course_title") or "Шаг обучения")
        data["why"] = str(data.get("why") or data.get("description") or "")
        if "career_boost" not in data and "boost" in data:
            data["career_boost"] = data["boost"]
        return data

    @field_validator("duration_hours", mode="before")
    @classmethod
    def normalize_duration(cls, value: Any) -> Any:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            digits = "".join(char for char in value if char.isdigit())
            return int(digits) if digits else None
        return value

    @property
    def boost(self) -> str:
        return self.career_boost


class RoadmapDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title_text: str | None = Field(default=None, alias="title")
    summary: str
    estimated_weeks: int | None = None
    career_opportunities: list[str] = Field(default_factory=list)
    items: list[RoadmapItemDTO] = Field(alias="steps")
    courses: list[RoadmapCourseDTO] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_roadmap(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = dict(value)
        data["summary"] = str(data.get("summary") or data.get("title") or "Роадмап обучения")
        if "steps" not in data and "items" in data:
            data["steps"] = data["items"]
        if "steps" not in data:
            data["steps"] = []
        return data

    @field_validator("estimated_weeks", mode="before")
    @classmethod
    def normalize_weeks(cls, value: Any) -> Any:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            digits = "".join(char for char in value if char.isdigit())
            return int(digits) if digits else None
        return value

    @property
    def title(self) -> str:
        return self.title_text or self.summary


class NeuralRoadmapResponseDTO(BaseModel):
    search_request: SearchRequestDTO = Field(default_factory=SearchRequestDTO)
    refined_search_request: RefinedSearchRequestDTO | None = None
    search_fallback_used: bool = False
    courses: list[RoadmapCourseDTO] = Field(default_factory=list)
    roadmap: RoadmapDTO
