from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from core.prompt_builder import (
    get_questions_for_age, build_prompt, personalize_question, 
    user_seems_confused, build_explanation_prompt, extract_option_from_llm_response
)
from services.llm_chat import query_llm
from db.mongo_handler import store_response, create_or_resume_test, login_child_by_code
from db.vector_store import embed_text, store_vector
from core.context_tracker import extract_context, update_super_context
import uuid

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

def is_direct_answer(user_input: str) -> str:
    """Check if user gave a direct SDQ answer and return the normalized option"""
    user_lower = user_input.lower().strip()
    
    # Check for exact matches
    if "not true" in user_lower:
        return "Not True"
    elif "certainly true" in user_lower:
        return "Certainly True"
    elif "somewhat true" in user_lower:
        return "Somewhat True"
    
    # Check for single word answers
    if user_lower in ["nottrue", "certainlytrue", "somewhattrue"]:
        if user_lower == "nottrue":
            return "Not True"
        elif user_lower == "certainlytrue":
            return "Certainly True"
        elif user_lower == "somewhattrue":
            return "Somewhat True"
    
    return None

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
        # Validate required fields
        if not req.test_id or not req.child_id:
            raise HTTPException(status_code=400, detail="test_id and child_id are required")
            
        questions = get_questions_for_age(req.age)
        index = req.question_index
        user_msg = req.chat_history[-1]["content"].strip() if req.chat_history else ""

        # 1. Handle confusion — explain question simply via LLM
        if user_seems_confused(user_msg) and 0 <= index < len(questions):
            explanation_prompt = build_explanation_prompt(
                questions[index], 
                req.child_name, 
                req.respondent_type
            )
            simplified = query_llm(explanation_prompt)
            return {
                "message": f"No problem! {simplified.strip()}\n\nSo, how would you answer: Not True, Somewhat True, or Certainly True?",
                "question_index": index,
                "child_name": req.child_name,
                "child_id": req.child_id,
                "test_id": req.test_id,
                "respondent_type": req.respondent_type
            }

        # 2. Extract context
        context = extract_context(req.chat_history)
        super_context = update_super_context({}, user_msg)

        # 3. Start test
        if index == -1 and any(x in user_msg.lower() for x in ["yes", "start", "go", "ready", "begin", "lets"]):
            question = questions[0]
            personalized = personalize_question(question, req.child_name, req.respondent_type)
            return {
                "message": personalized,
                "question_index": 0,
                "child_name": req.child_name,
                "child_id": req.child_id,
                "test_id": req.test_id,
                "respondent_type": req.respondent_type
            }

        # 4. Test complete
        if index is None or index >= len(questions):
            return {
                "message": "Thank you for completing the test!",
                "question_index": None,
                "child_id": req.child_id,
                "completed": True,
                "test_id": req.test_id,
                "respondent_type": req.respondent_type
            }

        # 5. **NEW: Check for direct answer FIRST**
        direct_answer = is_direct_answer(user_msg)
        if direct_answer and 0 <= index < len(questions):
            # User gave a direct answer - store it and move to next question
            store_response(req.test_id, index, questions[index], direct_answer)
            
            next_index = index + 1
            if next_index >= len(questions):
                return {
                    "message": "Perfect! Thank you for completing the questionnaire.",
                    "question_index": None,
                    "child_id": req.child_id,
                    "completed": True,
                    "test_id": req.test_id,
                    "respondent_type": req.respondent_type
                }
            
            next_q = personalize_question(questions[next_index], req.child_name, req.respondent_type)
            return {
                "message": f"Got it! Next question:\n\n{next_q}",
                "question_index": next_index,
                "child_name": req.child_name,
                "child_id": req.child_id,
                "test_id": req.test_id,
                "respondent_type": req.respondent_type
            }

        # 6. User confirms LLM suggestion
        if req.suggested_option and any(word in user_msg.lower() for word in ["confirm", "yes", "correct", "right", "sounds good", "that's right"]):
            # Extract the actual option from the suggested_option
            selected_option = extract_option_from_llm_response(req.suggested_option)
            store_response(req.test_id, index, questions[index], selected_option)
            
            next_index = index + 1
            if next_index >= len(questions):
                return {
                    "message": "Perfect! Thank you for completing the questionnaire.",
                    "question_index": None,
                    "child_id": req.child_id,
                    "completed": True,
                    "test_id": req.test_id,
                    "respondent_type": req.respondent_type
                }
            
            next_q = personalize_question(questions[next_index], req.child_name, req.respondent_type)
            return {
                "message": f"Great! Next question:\n\n{next_q}",
                "question_index": next_index,
                "child_name": req.child_name,
                "child_id": req.child_id,
                "test_id": req.test_id,
                "respondent_type": req.respondent_type
            }

        # 7. Handle user corrections/clarifications
        if req.suggested_option and any(word in user_msg.lower() for word in ["no", "wrong", "not right", "actually"]):
            # User is correcting the previous suggestion, get new interpretation
            pass  # Continue to step 8 to get new LLM analysis

        # 8. Store response to vector DB for memory/context
        user_text = req.chat_history[-1]["content"] if req.chat_history else ""
        vector = embed_text(user_text)
        store_vector(req.test_id, index, vector, user_text)

        # 9. Get LLM interpretation (only for descriptive answers)
        prompt = build_prompt(
            age=req.age,
            question_index=index,
            chat_history=req.chat_history,
            child_name=req.child_name,
            respondent_type=req.respondent_type,
            is_analysis=True
        )
        llm_output = query_llm(prompt)

        # Extract the actual option for storage
        interpreted_option = extract_option_from_llm_response(llm_output)

        return {
            "message": llm_output.strip(),
            "question_index": index,
            "child_name": req.child_name,
            "child_id": req.child_id,
            "suggested_option": interpreted_option,  # Store the clean option
            "test_id": req.test_id,
            "respondent_type": req.respondent_type
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
            return {
                "message": "Test completed.", 
                "completed": True,
                "child_id": req.child_id,
                "test_id": req.test_id,
                "respondent_type": req.respondent_type
            }

        return {
            "message": personalize_question(questions[next_index], req.child_name, req.respondent_type),
            "question_index": next_index,
            "child_id": req.child_id,
            "test_id": req.test_id,
            "completed": False,
            "respondent_type": req.respondent_type
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))