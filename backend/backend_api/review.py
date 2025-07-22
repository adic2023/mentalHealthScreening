# backend_api/review.py
from db.mongo_handler import get_final_review_for_user
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.mongo_handler import (
    get_pending_reviews,
    get_completed_reviews,
    get_full_review,
    submit_review
)

router = APIRouter()

# GET /review/pending
@router.get("/review/pending")
def pending_reviews():
    try:
        return get_pending_reviews()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /review/completed
@router.get("/review/completed")
def completed_reviews():
    try:
        return get_completed_reviews()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /review/{child_id}
@router.get("/review/{child_id}")
def fetch_full_review(child_id: str):
    try:
        return get_full_review(child_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# POST /review/submit
class SubmitReviewRequest(BaseModel):
    child_id: str
    psychologist_review: str
    reviewer_id: str

@router.post("/review/submit")
def review_submit(req: SubmitReviewRequest):
    try:
        submit_review(req.child_id, req.psychologist_review, req.reviewer_id)
        return { "message": "Review submitted successfully" }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /review-view/{child_id}
@router.get("/review-view/{child_id}")
def view_final_review(child_id: str):
    try:
        result = get_final_review_for_user(child_id)
        return result

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
