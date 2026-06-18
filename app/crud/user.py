from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    name: str,
    email: str,
    image_url: str | None = None
):
    user = User(
        name=name,
        email=email,
        image_url=image_url
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user