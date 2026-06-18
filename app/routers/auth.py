from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.user import GoogleUserRequest
from app.crud.user import (
    get_user_by_email,
    create_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/google")
def google_login(
    payload: GoogleUserRequest,
    db: Session = Depends(get_db)
):
    existing_user = get_user_by_email(
        db,
        payload.email
    )

    if existing_user:
        # Sync name or image_url if they changed
        updated = False
        if existing_user.name != payload.name:
            existing_user.name = payload.name
            updated = True
        if payload.image_url and existing_user.image_url != payload.image_url:
            existing_user.image_url = payload.image_url
            updated = True

        if updated:
            db.commit()
            db.refresh(existing_user)

        return {
            "message": "User already exists",
            "user": {
                "id": existing_user.id,
                "name": existing_user.name,
                "email": existing_user.email,
                "image_url": existing_user.image_url,
            }
        }

    user = create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        image_url=payload.image_url,
    )

    return {
        "message": "User created",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "image_url": user.image_url,
        }
    }