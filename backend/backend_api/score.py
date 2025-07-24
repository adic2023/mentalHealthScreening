# backend_api/score.py

from fastapi import APIRouter, HTTPException

# Reverse scoring indices (0-based)
reverse_indices = [6, 19, 13, 20, 24]

# SDQ subscale definitions for detailed analysis (optional)
EMOTIONAL = [2, 7, 12, 15, 23]
CONDUCT = [4, 6, 11, 17, 21]
HYPERACTIVITY = [1, 9, 14, 20, 24]
PEER = [5, 10, 13, 18, 23]
PROSOCIAL = [0, 3, 8, 16, 19]

# Normal scoring
OPTION_SCORES = {
    "Not True": 0,
    "Somewhat True": 1,
    "Certainly True": 2,
}

# Reverse scoring
REVERSE_OPTION_SCORES = {
    "Not True": 2,
    "Somewhat True": 1,
    "Certainly True": 0,
}

def calculate_score(test_id: str):
    """
    Calculate SDQ scores using your simplified logic
    """
    from db.mongo_handler import get_test_by_id
    
    try:
        test = get_test_by_id(test_id)
        confirm_options = test.get("confirm_options", [])
        
        if not confirm_options:
            raise Exception("No responses found for this test")
        
        total_score = 0
        
        # Calculate total score using your logic
        for response in confirm_options:
            question_index = response.get("question_index")
            selected_option = response.get("selected_option")
            
            if question_index in reverse_indices:
                # Reverse scoring for specific questions
                total_score += REVERSE_OPTION_SCORES.get(selected_option, 0)
            else:
                # Normal scoring
                total_score += OPTION_SCORES.get(selected_option, 0)
        
        # Calculate subscale scores for detailed analysis (optional)
        subscale_scores = {}
        response_map = {r.get("question_index"): r.get("selected_option") for r in confirm_options}
        
        for subscale_name, indices in {
            "emotional": EMOTIONAL,
            "conduct": CONDUCT, 
            "hyperactivity": HYPERACTIVITY,
            "peer": PEER,
            "prosocial": PROSOCIAL
        }.items():
            subscale_score = 0
            for idx in indices:
                if idx in response_map:
                    selected = response_map[idx]
                    if idx in reverse_indices:
                        subscale_score += REVERSE_OPTION_SCORES.get(selected, 0)
                    else:
                        subscale_score += OPTION_SCORES.get(selected, 0)
            
            subscale_scores[subscale_name] = subscale_score
        
        return {
            "test_id": test_id,
            "total_score": total_score,
            "response_count": len(confirm_options),
            "subscale_scores": subscale_scores,
            "max_possible_score": 50,  # 25 questions × 2 max points
            "calculated_at": __import__('datetime').datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error calculating score for test {test_id}: {str(e)}")
        raise Exception(f"Score calculation failed: {str(e)}")

# FastAPI router for API endpoints
router = APIRouter()

@router.get("/score/{test_id}")
def calculate_score_api(test_id: str):
    """API endpoint to calculate and return SDQ scores"""
    try:
        return calculate_score(test_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))