from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime,
    JSON
)
from sqlalchemy.sql import func

from app.db.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    resume_url = Column(String)

    jd_text = Column(String)

    match_score = Column(Integer)

    ats_score = Column(Integer)

    analysis_json = Column(JSON)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )