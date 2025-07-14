from fastapi import APIRouter, HTTPException
from db.mongo_handler import get_test_by_id

router=APIRouter()
@router.get("/history/{test_id}")
def get_chat_history(test_id:str):
    try:
        test = get_test_by_id(test_id)
        return {"chat_history": test.get("responses",[])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
'''
in chat
inside respond after llm_output = query_llm(prompt)

add::

from db.vector_store import embed_text, store_vector

user_text = req.chat_history[-1]["content"] if req.chat_history else ""
vector = embed_text(user_text)
store_vector(test_id="optional", question_index=question_index, vector=vector, text=user_text)

'''