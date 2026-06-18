# app/schemas/user.py

from pydantic import BaseModel

class GoogleUserRequest(BaseModel):
    name: str
    email: str
    image_url: str | None = None