# backend_api/child.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.mongo_handler import register_child, login_child_by_code

import uuid

router = APIRouter()

class ChildRegisterRequest(BaseModel):
    name: str
    age: int
    gender: str
    first_time: bool

class ChildLoginRequest(BaseModel):
    code: str

@router.post("/child/register")
def register(req: ChildRegisterRequest):
    try:
        if req.first_time:
            child_id = str(uuid.uuid4())
            code = str(uuid.uuid4())[:6]  # generate short code
            register_child(child_id, req.name, req.age, req.gender, code)
        else:
            # if returning, we return based on code
            child_data = login_child_by_code(req.code)
            if not child_data:
                raise Exception("Invalid code.")
            return {
                "child_id": child_data["child_id"],
                "name": child_data["name"],
                "age": child_data["age"]
            }

        return {
            "child_id": child_id,
            "code": code,
            "message": "Child registered successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/child/login")
def login(req: ChildLoginRequest):
    try:
        child_data = login_child_by_code(req.code)
        if not child_data:
            raise Exception("Invalid code.")

        return {
            "child_id": child_data["child_id"],
            "name": child_data["name"],
            "age": child_data["age"]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
