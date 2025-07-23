from fastapi import APIRouter, HTTPException

OPTION_SCORES = {
    "Not True": 0,
    "Somewhat True": 1,
    "Certainly True": 2
}

# ✅ Pure scoring logic with delayed import
def calculate_score(test_id: str):
    from db.mongo_handler import get_test_by_id  # <-- Moved import inside function

    test = get_test_by_id(test_id)
    confirm_options = test.get("confirm_options", [])
    total_score = sum(
        OPTION_SCORES.get(r.get("selected_option"), 0)
        for r in confirm_options
    )
    return {
        "test_id": test_id,
        "total_score": total_score,
        "response_count": len(confirm_options)
    }

# ✅ FastAPI route to expose the logic as an endpoint
router = APIRouter()

@router.get("/score/{test_id}")
def calculate_score_api(test_id: str):
    try:
        return calculate_score(test_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
