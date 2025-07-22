from pymongo import MongoClient
from datetime import datetime
from backend_api.score import calculate_score

client = MongoClient("mongodb://localhost:27017")
db = client["sdq_test_db"]

tests_collection = db["tests"]
children_collection = db["children"]

# ---------------------------- MODIFIED ----------------------------
def create_test_entry(test_id, age, child_name, child_id, respondent_type):
    print("Inserting test_id into Mongo:", test_id)
    tests_collection.insert_one({
        "test_id": test_id,
        "age": age,
        "child_name": child_name,
        "child_id": child_id,
        "respondent_type": respondent_type,
        "submitted": False,
        "confirm_options": [],
        "vector_responses": [],
        "created_at": datetime.utcnow()
    })

# ---------------------------- NEW ----------------------------
def register_child(child_id, name, age, gender, code):
    children_collection.insert_one({
        "child_id": child_id,
        "name": name,
        "age": age,
        "gender": gender,
        "code": code,
        "registered_on": datetime.utcnow()
    })

def login_child_by_code(code):
    return children_collection.find_one({ "code": code })

# ---------------------------- UNCHANGED ----------------------------
def store_response(test_id, question_index, question, selected_option):
    if "'" in selected_option:
        selected_option = selected_option.split("'")[1]

    tests_collection.update_one(
        { "test_id": test_id },
        {
            "$push": {
                "confirm_options": {
                    "question_index": question_index,
                    "question": question,
                    "selected_option": selected_option
                }
            }
        }
    )

def store_vector_response(test_id, question_index, vector, text):
    tests_collection.update_one(
        { "test_id": test_id },
        {
            "$push": {
                "vector_responses": {
                    "question_index": question_index,
                    "text": text,
                    "embedding": vector
                }
            }
        }
    )
    
def mark_test_submitted(test_id):
    result = tests_collection.update_one(
        {"test_id": test_id},
        {"$set": {"submitted": True}}
    )
    return result.modified_count > 0

def generate_score(test_id):
    # This is a placeholder for your actual scoring logic
    test = tests_collection.find_one({"test_id": test_id})
    confirm_options = test.get("confirm_options", [])

    # TODO: Plug in real SDQ scoring logic here
    score = {
        "emotional": 4,
        "conduct": 3,
        "hyperactivity": 5,
        "peer": 2,
        "prosocial": 6,
        "total_difficulties": 14
    }

    tests_collection.update_one(
        {"test_id": test_id},
        {"$set": {"score": score}}
    )

def check_all_submitted(child_id):
    submitted_roles = tests_collection.find({
        "child_id": child_id,
        "submitted": True
    }).distinct("respondent_type")

    return all(role in submitted_roles for role in ["child", "parent", "teacher"])

def create_review_if_ready(test_id):
    test = tests_collection.find_one({"test_id": test_id})
    child_id = test["child_id"]

    if not check_all_submitted(child_id):
        return False

    # Check if review already exists
    existing = db["reviews"].find_one({"child_id": child_id})
    if existing:
        return False

    # Get all test_ids
    all_tests = list(tests_collection.find({"child_id": child_id}))
    test_ids = {t["respondent_type"]: t["test_id"] for t in all_tests}

    # Generate combined AI summary (placeholder)
    summary = "This is an auto-generated summary based on all responses."

    db["reviews"].insert_one({
        "child_id": child_id,
        "test_ids": test_ids,
        "scores": {t["respondent_type"]: t["score"] for t in all_tests},
        "ai_generated_summary": summary,
        "status": "pending",
        "psychologist_review": None,
        "reviewed_by": None,
        "submitted_at": datetime.utcnow()
    })

    return True

def get_review_status(child_id):
    review = db["reviews"].find_one({"child_id": child_id})
    if not review:
        return { "status": "waiting", "message": "Review not generated yet." }

    return {
        "status": review["status"],
        "summary": review["ai_generated_summary"] if review["status"] == "reviewed" else None
    }

def generate_score(test_id):

    score = calculate_score(test_id)   # ← call Ansh’s function

    # Save it inside the corresponding test
    tests_collection.update_one(
        {"test_id": test_id},
        {"$set": {"score": score}}
    )

def get_pending_reviews():
    reviews = db["reviews"].find({ "status": "pending" })
    return [ { "child_id": r["child_id"], "submitted_at": r["submitted_at"] } for r in reviews ]

def get_completed_reviews():
    reviews = db["reviews"].find({ "status": "reviewed" })
    return [ { "child_id": r["child_id"], "reviewed_by": r["reviewed_by"] } for r in reviews ]

def get_full_review(child_id):
    review = db["reviews"].find_one({ "child_id": child_id })
    if not review:
        raise Exception("Review not found.")

    # Optionally fetch chat history per test_id if frontend needs it
    tests = db["tests"].find({ "test_id": { "$in": list(review["test_ids"].values()) } })
    test_map = { t["respondent_type"]: t for t in tests }

    return {
        "child_id": review["child_id"],
        "test_ids": review["test_ids"],
        "scores": review["scores"],
        "ai_summary": review["ai_generated_summary"],
        "status": review["status"],
        "psychologist_review": review["psychologist_review"],
        "tests": test_map  # includes confirm_options + vector_responses
    }

def submit_review(child_id, summary, reviewer_id):
    db["reviews"].update_one(
        { "child_id": child_id },
        {
            "$set": {
                "status": "reviewed",
                "psychologist_review": summary,
                "reviewed_by": reviewer_id
            }
        }
    )

def get_final_review_for_user(child_id):
    review = db["reviews"].find_one({ "child_id": child_id })

    if not review:
        raise Exception("No review found for this child.")

    if review["status"] != "reviewed":
        return { "status": "pending", "message": "Review not yet completed by psychologist." }

    return {
        "status": "reviewed",
        "summary": review["psychologist_review"]
    }
