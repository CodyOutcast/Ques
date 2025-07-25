from fastapi import APIRouter
from pydantic import BaseModel
from dependencies.auth import create_access_token

router = APIRouter()

class LoginInput(BaseModel):
    user_id: int  # For testing; in real app, use username/password

@router.post("/token")
def login(input: LoginInput):
    access_token = create_access_token({"sub": str(input.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}