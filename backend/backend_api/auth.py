# backend_api/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.mongo_handler import create_user, get_user_by_email

router = APIRouter()

class SignupRequest(BaseModel):
    email: str
    password: str
    role: str  # "parent", "teacher", "psychologist"

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str  # Added to verify role match

@router.post("/auth/signup")
def signup(req: SignupRequest):
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # Save raw password for now (no hashing)
    create_user(req.email, req.password, req.role)
    return {"message": "Signup successful"}

@router.post("/auth/login")
def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user or user["password_hash"] != req.password or user["role"] != req.role:
        raise HTTPException(status_code=401, detail="Invalid credentials or mismatched role")

    return {
        "message": "Login successful",
        "role": user["role"],
        "user_id": str(user["_id"])
    }