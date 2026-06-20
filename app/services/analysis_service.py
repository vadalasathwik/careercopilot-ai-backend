import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.services.gemini_service import analyze_resume_against_jd

def run_analysis_flow(db: Session, analysis_id: int) -> Analysis:
    # 1. Load analysis
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found."
        )

    # 2. Load linked resume
    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {analysis.resume_id} linked to this analysis not found."
        )

    # 3. Get resume_text
    resume_text_raw = resume.resume_text
    if not resume_text_raw or not resume_text_raw.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The linked resume has no extracted text. Please parse or re-upload the resume."
        )

    # Truncate texts to prevent excessive token usage
    resume_text = resume_text_raw[:15000]
    job_description = analysis.job_description[:8000]

    # 4. Send to Gemini & 5. Parse JSON
    try:
        gemini_result = analyze_resume_against_jd(resume_text, job_description)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini analysis execution failed: {str(e)}"
        )

    # Validate output format before updating the database
    ats_score = gemini_result.get("ats_score")
    match_score = gemini_result.get("match_score")
    missing_skills = gemini_result.get("missing_skills")
    recommendations = gemini_result.get("recommendations")

    # Perform strict type validations
    if not isinstance(ats_score, int):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: 'ats_score' must be an integer, got {type(ats_score).__name__}."
        )
    if not (0 <= ats_score <= 100):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: 'ats_score' must be between 0 and 100, got {ats_score}."
        )

    if not isinstance(match_score, int):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: 'match_score' must be an integer, got {type(match_score).__name__}."
        )
    if not (0 <= match_score <= 100):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: 'match_score' must be between 0 and 100, got {match_score}."
        )

    if not isinstance(missing_skills, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: 'missing_skills' must be a list, got {type(missing_skills).__name__}."
        )
    if not isinstance(recommendations, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: 'recommendations' must be a list, got {type(recommendations).__name__}."
        )

    # 6. Update analysis record
    analysis.ats_score = ats_score
    analysis.match_score = match_score
    analysis.missing_skills = json.dumps(missing_skills)
    analysis.recommendations = json.dumps(recommendations)

    db.commit()
    db.refresh(analysis)

    # 7. Return analysis result
    return analysis
