from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from core.prompt_builder import (
    get_questions_for_age, convert_to_first_person, format_question, build_question_prompt, 
    build_system_instruction, build_analysis_prompt, build_explanation_prompt, extract_option_from_llm_response

)   
from services.llm_chat import query_llm
from db.mongo_handler import store_response, create_or_resume_test, login_child_by_code
from db.vector_store import embed_text, store_vector
from core.context_tracker import extract_context, update_super_context
import uuid
from utils.intent_classifier import detect_user_intent
from db.mongo_handler import get_test_by_id, mark_test_submitted

router = APIRouter()

class StartRequest(BaseModel):
    age: int
    child_name: str
    child_id: Optional[str] = None  # Make optional - will be validated from child_code
    child_code: Optional[str] = None  # Child sharing code
    respondent_type: str  # "child" / "parent" / "teacher"
    email: str

class RespondRequest(BaseModel):
    age: int
    question_index: int
    chat_history: List[Dict[str, str]]
    child_name: str
    child_id: str  # Required for grouping
    respondent_type: Optional[str] = "parent"  # Made optional with default
    suggested_option: Optional[str] = None
    test_id: str  # Required - created in /start

class ConfirmOptionRequest(BaseModel):
    test_id: str
    child_id: str
    age: int
    question_index: int
    selected_option: str
    respondent_type: Optional[str] = "parent"  # Made optional with default

@router.post("/start")
def start_test(req: StartRequest):
    try:
        # Validate child using either child_id or child_code
        if req.child_code:
            # Parent/Teacher using sharing code
            child_data = login_child_by_code(req.child_code)
            if not child_data:
                raise HTTPException(status_code=400, detail="Invalid child code. Please verify the code.")
            
            child_id = child_data["child_id"]
            child_name = child_data["name"]
            age = child_data["age"]
            
        elif req.child_id:
            # Direct child_id provided (for child themselves)
            child_id = req.child_id
            child_name = req.child_name
            age = req.age
            
        else:
            raise HTTPException(status_code=400, detail="Either child_id or child_code is required")
        
        # Create new test or resume existing incomplete test
        test_result = create_or_resume_test(
            child_id=child_id,
            age=age,
            child_name=child_name,
            respondent_type=req.respondent_type,
            email=req.email
        )

        return {
            "test_id": test_result["test_id"],
            "child_id": child_id,
            "message": f"Hello! I'm here to guide you through a short behavioral questionnaire about {child_name if req.respondent_type != 'child' else 'yourself'}. Shall we begin? Type 'yes' to start.",
            "question_index": -1,
            "child_name": child_name,
            "age": age,
            "is_new_test": test_result["is_new"],
            "respondent_type": req.respondent_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/respond")
async def respond(req: RespondRequest):
    try:
        if not req.test_id or not req.child_id:
            raise HTTPException(status_code=400, detail="Missing test_id or child_id")

        test_data = get_test_by_id(req.test_id)
        if test_data.get("submitted"):
            return {
                "message": "This test has already been submitted. No further responses are needed.",
                "completed": True,
                "question_index": None
            }

        questions = get_questions_for_age(req.age)
        index = req.question_index
        user_msg = req.chat_history[-1]["content"].strip() if req.chat_history else ""

        if not user_msg:
            return {"message": "Can you share more about this?", "question_index": index}

        # ⏺️ Store vector representation for review
        vector = embed_text(user_msg)
        store_vector(req.test_id, max(0, index), vector, user_msg)

        # ▶️ Start test if index = -1 and user agrees
        if index == -1 and any(x in user_msg.lower() for x in ["yes", "start", "go", "ready", "begin"]):
            first_q = questions[0]
            q_text = build_question_prompt(first_q, req.child_name, req.respondent_type)
            return {
                "message": q_text,
                "question_index": 0,
                "child_id": req.child_id,
                "test_id": req.test_id,
                "respondent_type": req.respondent_type
            }

        # ✅ End of test check - FIXED: Don't mark as submitted here
        if index is None or index >= len(questions):
            return {
                "message": "Thank you for completing all questions! You can now submit your test responses.",
                "question_index": None,
                "completed": True,
                "test_id": req.test_id
            }

        # 🧠 Detect user intent
        user_intent = detect_user_intent(req.chat_history)

        current_question = questions[index]

        # --- Intent-based handling ---
        if user_intent == "confused" or user_intent == "asking_question":
            explain_prompt = build_explanation_prompt(current_question, req.child_name, req.respondent_type)
            explanation = query_llm(explain_prompt)
            return {
                "message": f"No worries! {explanation.strip()}\n\nSo how would you answer: Not True / Somewhat True / Certainly True?",
                "question_index": index,
                "child_id": req.child_id,
                "test_id": req.test_id
            }

        elif user_intent == "confirmation" and req.suggested_option:
            final_option = extract_option_from_llm_response(req.suggested_option)
            store_response(req.test_id, index, current_question, final_option)

            next_index = index + 1
            if next_index >= len(questions):
                # FIXED: Don't mark as submitted, just return completion message
                return {
                    "message": "Perfect! That was the last question. All questions completed! You can now submit your test responses.",
                    "question_index": None,
                    "completed": True
                }

            next_q = questions[next_index]
            next_q_prompt = build_question_prompt(next_q, req.child_name, req.respondent_type)
            return {
                "message": f"Great! Next question:\n\n{next_q_prompt}",
                "question_index": next_index,
                "suggested_option": None
            }

        elif user_intent == "correction":
            # Re-analyze from new input
            prompt = build_analysis_prompt(
                age=req.age,
                question_index=index,
                chat_history=req.chat_history,
                child_name=req.child_name,
                respondent_type=req.respondent_type
            )
            llm_output = query_llm(prompt)
            new_suggestion = extract_option_from_llm_response(llm_output)
            return {
                "message": f"{llm_output.strip()}\n\n",
                "question_index": index,
                "suggested_option": new_suggestion
            }

        elif user_intent == "direct_answer":
            clean_option = extract_option_from_llm_response(user_msg)
            store_response(req.test_id, index, current_question, clean_option)

            next_index = index + 1
            if next_index >= len(questions):
                # FIXED: Don't mark as submitted, just return completion message
                return {
                    "message": "Thanks! That was the last question. All questions completed! You can now submit your test responses.",
                    "question_index": None,
                    "completed": True
                }

            next_q = questions[next_index]
            next_q_prompt = build_question_prompt(next_q, req.child_name, req.respondent_type)
            return {
                "message": f"Got it – '{clean_option}' noted.\n\nNext question:\n{next_q_prompt}",
                "question_index": next_index,
                "suggested_option": None
            }

        elif user_intent == "sharing_experience" or user_intent == "unclear":
            # Treat like open-ended input — analyze with LLM
            prompt = build_analysis_prompt(
                age=req.age,
                question_index=index,
                chat_history=req.chat_history,
                child_name=req.child_name,
                respondent_type=req.respondent_type
            )
            llm_output = query_llm(prompt)
            suggested = extract_option_from_llm_response(llm_output)
            return {
                "message": f"{llm_output.strip()}\n\n",
                "question_index": index,
                "suggested_option": suggested
            }

        # Fallback
        return {
            "message": "Sorry, I didn't understand that. Could you say it again?",
            "question_index": index
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm-option")
def confirm_option(req: ConfirmOptionRequest):

    try:
        questions = get_questions_for_age(req.age)
        if req.question_index >= len(questions):
            raise HTTPException(status_code=400, detail="Invalid question index.")

        test_data = get_test_by_id(req.test_id)
        if test_data.get("submitted"):
            return {
                "message": "This test has already been submitted.",
                "completed": True,
                "question_index": None
            }

        question = questions[req.question_index]
        store_response(
            test_id=req.test_id,
            question_index=req.question_index,
            question=question,
            selected_option=req.selected_option
        )

        next_index = req.question_index + 1
        if next_index >= len(questions):
            # FIXED: Don't mark as submitted here either
            return {
                "message": "Thanks! That was the final question. All questions completed! You can now submit your test responses.",
                "question_index": None,
                "completed": True,
                "test_id": req.test_id,
                "child_id": req.child_id,
                "respondent_type": req.respondent_type
            }

        next_question = get_questions_for_age(req.age)[next_index]
        next_prompt = build_question_prompt(next_question, req.child_name, req.respondent_type)

        return {
            "message": f"Next question:\n\n{next_prompt}",
            "question_index": next_index,
            "completed": False,
            "test_id": req.test_id,
            "child_id": req.child_id,
            "respondent_type": req.respondent_type
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))