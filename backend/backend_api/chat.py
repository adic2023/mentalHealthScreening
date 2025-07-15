from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from core.prompt_builder import get_questions_for_age, build_prompt, personalize_question
from services.llm_chat import query_llm
from db.mongo_handler import store_response, create_test_entry
from db.vector_store import embed_text, store_vector
from core.context_tracker import extract_context, update_super_context
import uuid

router = APIRouter()

class StartRequest(BaseModel):
    age: int
    child_name: str

class RespondRequest(BaseModel):
    age: int
    question_index: int
    chat_history: List[Dict[str, str]]
    child_name: str
    suggested_option: Optional[str] = None
    test_id: Optional[str] = None

class ConfirmOptionRequest(BaseModel):
    test_id: str
    age: int
    question_index: int
    selected_option: str

@router.post("/start")
def start_test(req: StartRequest):
    try:
        test_id = str(uuid.uuid4())
        create_test_entry(test_id, req.age, req.child_name)

        return {
            "test_id": test_id,
            "message": "Hello! I'm here to guide you through a short behavioral questionnaire for your child. Shall we begin? Type 'yes' to start.",
            "question_index": -1,
            "child_name": req.child_name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/respond")
async def respond(req: RespondRequest):
    try:
        questions = get_questions_for_age(req.age)
        index = req.question_index
        user_msg = req.chat_history[-1]["content"].lower() if req.chat_history else ""

        # handle test_id creation fallback
        test_id = req.test_id or str(uuid.uuid4())
        if req.test_id is None:
            create_test_entry(test_id, req.age, req.child_name)

        # Extract context
        context = extract_context(req.chat_history)
        super_context = update_super_context({}, user_msg)

        # Start test
        if index == -1 and any(x in user_msg for x in ["yes", "start", "go ahead", "ready"]):
            question = questions[0]
            personalized = personalize_question(question, req.child_name)
            return {
                "message": personalized,
                "question_index": 0,
                "child_name": req.child_name,
                "test_id": test_id
            }

        if index is None or index >= len(questions):
            return {
                "message": "Thank you for completing the test!",
                "question_index": None,
                "completed": True,
                "test_id": test_id
            }

        # Confirm and move to next
        if req.suggested_option and "confirm" in user_msg:
            store_response(test_id, index, questions[index], req.suggested_option)

            next_index = index + 1
            if next_index >= len(questions):
                return {
                    "message": "Thank you for completing the test!",
                    "question_index": None,
                    "completed": True,
                    "test_id": test_id
                }
            next_q = personalize_question(questions[next_index], req.child_name)
            return {
                "message": next_q,
                "question_index": next_index,
                "child_name": req.child_name,
                "test_id": test_id
            }

        # Store to vector DB
        user_text = req.chat_history[-1]["content"] if req.chat_history else ""
        vector = embed_text(user_text)
        store_vector(test_id, index, vector, user_text)

        # Get LLM option suggestion
        prompt = build_prompt(
            age=req.age,
            question_index=index,
            chat_history=req.chat_history,
            child_name=req.child_name,
            is_analysis=True
        )
        llm_output = query_llm(prompt)

        return {
            "message": f"It seems you're saying: '{llm_output}'. Type 'confirm' to proceed.",
            "question_index": index,
            "child_name": req.child_name,
            "suggested_option": llm_output,
            "test_id": test_id
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm-option")
def confirm_option(req: ConfirmOptionRequest):
    try:
        questions = get_questions_for_age(req.age)
        question = questions[req.question_index]

        store_response(
            test_id=req.test_id,
            question_index=req.question_index,
            question=question,
            selected_option=req.selected_option
        )

        next_index = req.question_index + 1
        if next_index >= len(questions):
            return {"message": "Test completed.", "completed": True}

        return {
            "message": personalize_question(questions[next_index], req.test_id),
            "question_index": next_index,
            "completed": False
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))