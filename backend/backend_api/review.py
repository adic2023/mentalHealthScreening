# backend_api/review.py - PSYCHOLOGIST DASHBOARD ONLY
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from bson import ObjectId
from db.mongo_handler import (
    get_pending_reviews,
    get_completed_reviews, 
    get_full_review,
    submit_review,
    get_results_by_child_id
)

router = APIRouter()

class SubmitReviewRequest(BaseModel):
    child_id: str
    psychologist_review: str
    reviewer_id: str

def convert_objectid(data):
    """Recursively convert ObjectId to string in dictionaries/lists."""
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {
            key: str(value) if isinstance(value, ObjectId) else convert_objectid(value)
            for key, value in data.items()
        }
    else:
        return data

# GET /review/pending - Psychologist sees pending reviews
@router.get("/reviews/pending")
def pending_reviews():
    """Get all tests pending psychologist review"""
    print("hello")
    try:
        return get_pending_reviews()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /review/completed  - Psychologist sees completed reviews
@router.get("/reviews/completed")
def completed_reviews():
    """Get all completed psychologist reviews"""
    try:
        return get_completed_reviews()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /review/{child_id} - Psychologist gets full details for review
@router.get("/reviews/{child_id}")
def fetch_full_review(child_id: str):
    """Get comprehensive test data for psychologist review"""
    try:
        data = get_full_review(child_id)
        return convert_objectid(data)  # 🔥 This fixes the serialization error
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# POST /review/submit - Psychologist submits their review
@router.post("/reviews/submit")
def review_submit(req: SubmitReviewRequest):
    """Submit psychologist review and recommendations"""
    try:
        submit_review(req.child_id, req.psychologist_review, req.reviewer_id)
        return {"message": "Review submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /review/{child_id} - Get completed review results for parents/teachers/children
@router.get("/review/{child_id}")
def get_completed_review_results(child_id: str, email: str = Query(...), role: str = Query(...)):
    """
    Get completed psychologist review and user's test scores for results page
    Used by parents/teachers/children to view their results after psychologist review is completed
    """
    try:
        results = get_results_by_child_id(child_id, email, role)
        if not results:
            return {"status": "pending"}
        results["status"] = "reviewed"
        return results
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))