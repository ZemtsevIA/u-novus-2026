from pydantic import BaseModel, ConfigDict, Field


class SearchRequestDTO(BaseModel):
    topic: str
    preferences: str | None = None
    level: str | None = None
    limit: int | None = None


class RefinedSearchRequestDTO(BaseModel):
    topic: str
    preferences: str | None = None
    level: str | None = None


class RoadmapCourseDTO(BaseModel):
    id: str
    title: str
    platform: str | None = None
    level: str | None = None
    format: str | None = None
    description: str | None = None
    url: str | None = None


class RoadmapItemDTO(BaseModel):
    step: int | None = None
    title: str
    course_id: str | None = None
    course_title: str | None = None
    course_url: str | None = None
    format: str | None = None
    duration_hours: int | None = None
    skills: list[str] = []
    why: str
    career_boost: str

    @property
    def boost(self) -> str:
        return self.career_boost


class RoadmapDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    summary: str
    estimated_weeks: int | None = None
    career_opportunities: list[str] = []
    items: list[RoadmapItemDTO] = Field(alias="steps")

    @property
    def title(self) -> str:
        return self.summary


class NeuralRoadmapResponseDTO(BaseModel):
    search_request: SearchRequestDTO
    refined_search_request: RefinedSearchRequestDTO | None = None
    search_fallback_used: bool = False
    courses: list[RoadmapCourseDTO] = []
    roadmap: RoadmapDTO
