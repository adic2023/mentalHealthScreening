# backend_api/test.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
from db.mongo_handler import (
    mark_test_submitted, check_all_submitted, generate_score, 
    create_review_if_ready, get_child_tests_summary, get_test_results_for_user,
    upsert_review_and_generate_summary
)

router = APIRouter()

class SubmitTestRequest(BaseModel):
    test_id: str

@router.post("/test/submit")
def submit_test(req: SubmitTestRequest):
    """
    Handle test submission with integrated scoring and review creation
    """
    try:
        print(f"Processing test submission for test_id: {req.test_id}")
        
        # Step 1: Mark this test as submitted
        updated = mark_test_submitted(req.test_id)
        if not updated:
            raise Exception("Test not found or could not be updated.")
        print(f"Test {req.test_id} marked as submitted")

        # Step 2: Generate and store score using your scoring logic
        try:
            score_data = generate_score(req.test_id)
            print(f"Score generated: {score_data}")
        except Exception as score_error:
            print(f"Score generation failed: {score_error}")
            # Continue even if scoring fails - can be retried later
            pass

        # Step 3: Check if all parties (child, parent, teacher) have submitted
        # If so, create the review document
        review_created = upsert_review_and_generate_summary(req.test_id)

        
        if review_created:
            print(f"Review document created for test {req.test_id}")
        else:
            print(f"Review not created - waiting for other parties to submit")

        # Return success response
        response = {
            "message": "Test submitted successfully.",
            "test_id": req.test_id,
            "score_generated": True,
            "review_created": review_created,
            "next_step": "Review pending with psychologist" if review_created else "Waiting for other parties to complete their assessments"
        }
        
        return response

    except Exception as e:
        print(f"Error in test submission: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/test/status/{child_id}")
def get_child_status(child_id: str):
    """Get the overall status of tests for a specific child"""
    try:
        from db.mongo_handler import get_review_status
        status = get_review_status(child_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/test/summary")
def get_dashboard_summary(email: str = Query(...), role: str = Query(...)):
    """
    Get dashboard summary for parent/teacher showing their test history
    This replaces the /review/summary endpoint for non-psychologists
    """
    try:
        # Get all tests taken by this user (parent/teacher) 
        summary = get_child_tests_summary(email, role)
        
        if not summary:
            return {
                "status": "not_started",
                "tests": [],
                "message": "No tests found for this user"
            }
        
        # Transform the data for frontend consumption
        tests = []
        for child_data in summary:
            # For each child, show their test status
            child_tests = child_data.get('tests', [])
            
            # Find this user's test for this child
            user_test = None
            for test in child_tests:
                if test.get('respondent_type') == role and test.get('email') == email:
                    user_test = test
                    break
            
            if user_test:
                # Determine overall status based on all tests for this child
                all_submitted = all(t.get('submitted', False) for t in child_tests)
                review_completed = child_data.get('review_status') == 'completed'
                
                if review_completed:
                    status = 'Review Completed'
                elif all_submitted:
                    status = 'Review Pending'  
                elif user_test.get('submitted', False):
                    status = 'Submitted - Waiting for Others'
                else:
                    status = 'In Progress'
                
                tests.append({
                    "child_id": child_data['child_id'],
                    "child_name": child_data.get('child_name', 'Unknown'),
                    "test_id": user_test['test_id'],
                    "date": user_test.get('created_at', ''),
                    "status": status,
                    "test_type": "SDQ",
                    "taken_by": role.title()
                })
        
        if not tests:
            return {
                "status": "not_started", 
                "tests": [],
                "message": "No tests found for this user"
            }
            
        return {
            "status": "has_tests",
            "tests": tests
        }
        
    except Exception as e:
        print(f"Error in dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/results/{child_id}")
def get_test_results(child_id: str, email: str = Query(...), role: str = Query(...)):
    """
    Get test results for a specific child (only if review is completed)
    This replaces the /review-view endpoint for non-psychologists
    """
    try:
        results = get_test_results_for_user(child_id, email, role)
        
        if not results:
            raise HTTPException(status_code=404, detail="Results not found or not yet reviewed")
            
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/child-code/{child_id}")
def get_child_code(child_id: str):
    """Get the sharing code for a child"""
    try:
        from db.mongo_handler import get_child_code
        code = get_child_code(child_id)
        if not code:
            raise HTTPException(status_code=404, detail="Child not found")
        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/score/{test_id}")
def get_test_score(test_id: str):
    """Get calculated score for a specific test"""
    try:
        from db.mongo_handler import get_test_by_id
        test = get_test_by_id(test_id)
        
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
            
        scores = test.get("scores")
        if not scores:
            # Try to generate score if it doesn't exist
            try:
                from db.mongo_handler import generate_score
                scores = generate_score(test_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Could not generate score: {str(e)}")
        
        return {
            "test_id": test_id,
            "scores": scores,
            "status": "completed" if test.get("submitted") else "in_progress"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))