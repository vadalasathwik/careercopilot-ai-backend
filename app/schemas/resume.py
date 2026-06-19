from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResumeCreate(BaseModel):
    user_id: int
    file_name: str
    file_url: str
    resume_text: str | None = None


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_url: str
    resume_text: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

