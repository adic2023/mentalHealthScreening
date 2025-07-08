from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionResponse(BaseModel):
    question_index: int
    question: str
    selected_option: str
    llm_summary: Optional[str] = None

class SDQTestEntry(BaseModel):
    test_id: str
    age: int
    child_name: str
    responses: List[QuestionResponse] = []
    created_at: datetime = datetime.utcnow()
