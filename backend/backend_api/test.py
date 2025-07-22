# backend_api/test.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.mongo_handler import mark_test_submitted, check_all_submitted, generate_score, create_review_if_ready

router = APIRouter()

class SubmitTestRequest(BaseModel):
    test_id: str

@router.post("/test/submit")
def submit_test(req: SubmitTestRequest):
    try:
        # Step 1: Mark this test as submitted
        updated = mark_test_submitted(req.test_id)
        if not updated:
            raise Exception("Test not found or could not be updated.")

        # Step 2: Trigger score calculation using Ansh's score.py
        generate_score(req.test_id)

        # Step 3: Check if child, parent, and teacher all submitted
        review_created = create_review_if_ready(req.test_id)

        # ⚠️ NOTE FOR FRONTEND:
        # After hitting this endpoint, show a "submitting..." loading screen.
        # Once it returns successfully, redirect user to "Thank you" or home.
        # DO NOT show score now — it is only visible after psychologist review.

        return {
            "message": "Test submitted successfully.",
            "review_created": review_created
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{child_id}")
def get_status(child_id: str):
    from db.mongo_handler import get_review_status
    try:
        status = get_review_status(child_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))