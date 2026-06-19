from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate


def create_analysis(db: Session, analysis: AnalysisCreate) -> Analysis:
    db_analysis = Analysis(
        user_id=analysis.user_id,
        resume_id=analysis.resume_id,
        job_description=analysis.job_description,
        ats_score=analysis.ats_score,
        match_score=analysis.match_score,
        missing_skills=analysis.missing_skills,
        recommendations=analysis.recommendations,
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


def get_user_analyses(db: Session, user_id: int) -> list[Analysis]:
    return db.query(Analysis).filter(Analysis.user_id == user_id).all()
