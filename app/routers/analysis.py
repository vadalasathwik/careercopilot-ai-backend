from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisCreateResponse
from app.crud.analysis import create_analysis, get_user_analyses
from app.services.analysis_service import run_analysis_flow

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post("/create", response_model=AnalysisCreateResponse)
def create_new_analysis(
    analysis_in: AnalysisCreate,
    db: Session = Depends(get_db)
):
    # 1. Check if user exists
    user = db.query(User).filter(User.id == analysis_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {analysis_in.user_id} not found."
        )

    # 2. Check if resume exists
    resume = db.query(Resume).filter(Resume.id == analysis_in.resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {analysis_in.resume_id} not found."
        )

    # 3. Check if resume belongs to user
    if resume.user_id != analysis_in.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume does not belong to the user."
        )

    # 4. Save analysis to DB
    db_analysis = create_analysis(db, analysis_in)
    return db_analysis


@router.get("/user/{user_id}", response_model=list[AnalysisResponse])
def get_analyses_for_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    analyses = get_user_analyses(db, user_id)
    return analyses


@router.post("/run/{analysis_id}", response_model=AnalysisResponse)
def run_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Triggers the ATS analysis for a specific analysis record by running
    the resume text and job description against the Gemini model.
    """
    return run_analysis_flow(db, analysis_id)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves the full analysis record by its ID.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found."
        )
    return analysis
