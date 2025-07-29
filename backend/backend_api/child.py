# backend_api/child.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.mongo_handler import register_child, login_child_by_code, get_child_by_id
from typing import Optional
import uuid

router = APIRouter()

class ChildRegisterRequest(BaseModel):
    name: str
    age: int
    gender: str
    first_time: bool
    code: Optional[str] = None
    email: str  # <-- this is now required
    
class ChildLoginRequest(BaseModel):
    code: str

@router.post("/child/register")
def register(req: ChildRegisterRequest):
    try:
        if req.first_time:
            # New child registration
            child_id = str(uuid.uuid4())
            code = str(uuid.uuid4())[:8].upper()  # 8-character code for easier sharing
            
            register_child(child_id, req.name, req.age, req.gender, code, req.email)
            
            return {
                "child_id": child_id,
                "code": code,
                "name": req.name,
                "age": req.age,
                "gender": req.gender,
                "message": "Child registered successfully! Share this code with parent and teacher.",
                "instructions": f"Share code '{code}' with the child's parent and teacher so they can also take the assessment."
            }
        else:
            # Returning user with existing code
            if not req.code:
                raise Exception("Code is required for returning users.")
                
            child_data = login_child_by_code(req.code)
            if not child_data:
                raise Exception("Invalid code. Please check and try again.")
                
            return {
                "child_id": child_data["child_id"],
                "code": req.code,
                "name": child_data["name"],
                "age": child_data["age"],
                "gender": child_data.get("gender", ""),
                "message": "Welcome back!",
                "existing_user": True
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/child/login")
def login(req: ChildLoginRequest):
    try:
        child_data = login_child_by_code(req.code)
        if not child_data:
            raise Exception("Invalid code. Please verify the code and try again.")
            
        return {
            "child_id": child_data["child_id"],
            "name": child_data["name"],
            "age": child_data["age"],
            "gender": child_data.get("gender", ""),
            "code": req.code,
            "message": "Login successful!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/child/{child_id}")
def get_child_details(child_id: str):
    """Get child details by child_id"""
    try:
        child_data = get_child_by_id(child_id)
        if not child_data:
            raise Exception("Child not found.")
            
        return {
            "child_id": child_data["child_id"],
            "name": child_data["name"],
            "age": child_data["age"],
            "gender": child_data.get("gender", ""),
            "code": child_data.get("code", ""),
            "created_at": child_data.get("created_at", "")
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/child/code/{code}")
def get_child_by_code(code: str):
    """Get child details by sharing code - useful for parent/teacher before starting test"""
    try:
        child_data = login_child_by_code(code)
        if not child_data:
            raise Exception("Invalid code. Please verify the code and try again.")
            
        return {
            "child_id": child_data["child_id"],
            "name": child_data["name"],
            "age": child_data["age"],
            "gender": child_data.get("gender", ""),
            "code": code,
            "message": "Child found! You can now start the assessment."
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))