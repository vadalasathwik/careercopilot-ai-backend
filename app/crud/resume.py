from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate


def create_resume(db: Session, resume: ResumeCreate) -> Resume:
    db_resume = Resume(
        user_id=resume.user_id,
        file_name=resume.file_name,
        file_url=resume.file_url,
        resume_text=resume.resume_text
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


def get_user_resumes(db: Session, user_id: int) -> list[Resume]:
    return db.query(Resume).filter(Resume.user_id == user_id).all()
