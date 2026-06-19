import os
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.models.user import User
from app.crud.resume import create_resume, get_user_resumes
from app.schemas.resume import ResumeCreate, ResumeResponse
from app.services.storage_service import upload_file_to_storage
from app.services.resume_parser import extract_resume_text

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    filename = file.filename or ""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only PDF and DOCX files are allowed."
        )

    # 2. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF and DOCX files are allowed."
        )

    # 3. Read content to check size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too large. Max allowed size is 5 MB."
        )

    # 4. Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    # 5. Upload file to Supabase Storage
    try:
        file_url = upload_file_to_storage(file_bytes, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to storage: {str(e)}"
        )

    # 6. Extract resume text
    try:
        resume_text = extract_resume_text(file_bytes, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from resume: {str(e)}"
        )

    # 7. Save metadata and text to DB
    resume_in = ResumeCreate(
        user_id=user_id,
        file_name=filename,
        file_url=file_url,
        resume_text=resume_text
    )
    db_resume = create_resume(db, resume_in)

    return db_resume


@router.get("/{user_id}", response_model=list[ResumeResponse])
def get_resumes(
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

    resumes = get_user_resumes(db, user_id)
    return resumes
