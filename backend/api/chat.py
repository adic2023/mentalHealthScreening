from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from core.prompt_builder import build_prompt, get_questions_for_age
from services.llm_chat import query_llm
from db.mongo_handler import store_response,create_test_entry
import uuid

router = APIRouter()

class StartRequest(BaseModel):
    age: int
    child_name: Optional[str] = "the child"

class RespondRequest(BaseModel):
    age: int
    question_index: int
    chat_history: List[Dict[str, str]]
    child_name: Optional[str] = "the child"

class ConfirmOptionRequest(BaseModel):
    test_id: str
    age: int
    question_index: int
    selected_option: str

@router.post("/start")
def start_test(req: StartRequest):
    try:
        test_id = str(uuid.uuid4())

        # 1. Store test info in MongoDB
        create_test_entry(
            test_id=test_id,
            age=req.age,
            child_name=req.child_name
        )

        # 2. Build initial prompt
        prompt = build_prompt(
            age=req.age,
            question_index=0,
            chat_history=[],
            child_name=req.child_name,
            is_first=True
        )

        return {
            "test_id": test_id,
            "message": prompt.split("Assistant:")[-1].strip(),
            "question_index": -1,
            "child_name": req.child_name,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/respond")
async def respond(req: RespondRequest):
    try:
        questions = get_questions_for_age(req.age)
        question_index = req.question_index
        user_last_message = req.chat_history[-1]["content"].lower() if req.chat_history else ""

        def user_just_agreed_to_start(msg):
            return any(phrase in msg for phrase in ["yes", "start", "ready", "go ahead", "okay"])

        if question_index == 0 and user_just_agreed_to_start(user_last_message):
            return {
                "message": questions[0],
                "clarification": None,
                "question_index": 0,
                "child_name": req.child_name
            }

        # Analysis mode to interpret user response into option
        prompt = build_prompt(
            age=req.age,
            question_index=question_index,
            chat_history=req.chat_history,
            child_name=req.child_name,
            is_analysis=True
        )

        llm_output = query_llm(prompt)  # returns e.g. "Certainly True"

        # Ask for confirmation from user
        return {
            "message": f"It seems you're saying: '{llm_output}'. Would you like to confirm this option or change it?",
            "clarification": None,
            "question_index": question_index,  # do NOT increment yet
            "child_name": req.child_name,
            "suggested_option": llm_output  # you may pass this to confirm later
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/confirm-option")
def confirm_option(req: ConfirmOptionRequest):
    try:
        questions = get_questions_for_age(req.age)
        question = questions[req.question_index]

        llm_summary = f"{req.selected_option} - interpreted answer for: '{question}'"

        store_response(
            test_id=req.test_id,
            question_index=req.question_index,
            question=question,
            selected_option=req.selected_option,
            llm_summary=llm_summary
        )

        next_index = req.question_index + 1

        if next_index >= len(questions):
            return {
                "message": "Test completed. Thank you!",
                "completed": True
            }

        next_question = questions[next_index]
        return {
            "message": next_question,
            "question_index": next_index,
            "completed": False
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
