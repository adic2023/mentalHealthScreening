
from fastapi import APIRouter,HTTPException
from db.mongo_handler import get_test_by_id

router =APIRouter()
OPTION_SCORES ={
    "Not True": 0,
    "Somewhat True": 1,
    "Certainly True": 2
}

@router.get("/score/{test_id}")
def calculate_score(test_id:str):
    try:
        test =get_test_by_id(test_id)
        responses =test.get("responses", [])
        total_score =sum(
            OPTION_SCORES.get(r.get("selected_option"), 0)
            for r in responses
        )
        return{
            "test_id": test_id,
            "total_score": total_score,
            "response_count": len(responses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''
main.py- 
(add new routes)
from api.chat import router as chat_router
from api.score import router as score_router
from api.history import router as history_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(score_router)
app.include_router(history_router)

''' 