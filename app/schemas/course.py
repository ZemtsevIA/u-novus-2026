from pydantic import BaseModel


class CourseDTO(BaseModel):
    id: str
    title: str
    url: str

