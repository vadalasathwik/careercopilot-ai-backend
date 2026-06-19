from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AnalysisCreate(BaseModel):
    user_id: int
    resume_id: int
    job_description: str
    ats_score: int | None = None
    match_score: int | None = None
    missing_skills: str | None = None
    recommendations: str | None = None


class AnalysisCreateResponse(BaseModel):
    id: int


class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_description: str
    ats_score: int | None = None
    match_score: int | None = None
    missing_skills: str | None = None
    recommendations: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
