from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["sdq_test_db"]
collection = db["tests"]

def create_test_entry(test_id, age, child_name):
    print("Inserting test_id into Mongo:", test_id)
    collection.insert_one({
        "test_id": test_id,
        "age": age,
        "child_name": child_name,
        "responses": [],
        "created_at": datetime.utcnow()
    })

def store_response(test_id, question_index, question, selected_option, llm_summary=None):
    collection.update_one(
        {"test_id": test_id},
        {
            "$push": {
                "responses": {
                    "question_index": question_index,
                    "question": question,
                    "selected_option": selected_option,
                    "llm_summary": llm_summary
                }
            }
        }
    )
