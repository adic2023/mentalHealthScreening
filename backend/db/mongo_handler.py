# db/mongo_handler.py
from pymongo import MongoClient
from datetime import datetime
from services.llm_chat import query_llm
from core.prompt_builder import build_summary_prompt, get_questions_for_age
from bson import ObjectId

def clean_mongo_obj(doc):
    """Convert ObjectId to string and handle other non-JSON-safe types."""
    if not doc:
        return doc
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    return doc

client = MongoClient("mongodb://localhost:27017")
db = client["sdq_test_db"]

tests_collection = db["tests"]
children_collection = db["children"]
users_collection = db["users"]
reviews_collection = db["reviews"]
vector_responses_collection = db["vector_responses"]

# ---------------------------- AUTHENTICATION ----------------------------
def create_user(email, password_hash, role):
    user = {
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.utcnow()
    }
    users_collection.insert_one(user)

def get_user_by_email(email):
    return users_collection.find_one({"email": email})

# ---------------------------- CHILD REGISTRATION FUNCTIONS ----------------------------
def register_child(child_id, name, age, gender, code, email):
    children_collection.insert_one({
        "child_id": child_id,
        "name": name,
        "age": age,
        "gender": gender,
        "code": code,
        "email": email,
        "registered_on": datetime.utcnow()
    })

def login_child_by_code(code):
    return children_collection.find_one({"code": code})

def get_child_by_id(child_id):
    """Get child data by child_id"""
    return children_collection.find_one({"child_id": child_id})

def get_child_code(child_id):
    """Get sharing code for a child"""
    child = children_collection.find_one({"child_id": child_id})
    return child.get("code") if child else None

# ---------------------------- DASHBOARD FUNCTIONS ----------------------------
def get_child_tests_summary(email, role):
    """Get dashboard summary for parent/teacher - groups tests by child"""
    try:
        user_tests = list(tests_collection.find({
            "email": email,
            "respondent_type": role
        }))
        
        if not user_tests:
            return None
            
        children_data = {}
        
        for test in user_tests:
            child_id = test["child_id"]
            
            if child_id not in children_data:
                child_info = get_child_by_id(child_id)
                children_data[child_id] = {
                    "child_id": child_id,
                    "child_name": child_info.get("name", "Unknown") if child_info else "Unknown",
                    "tests": [],
                    "review_status": "pending"
                }
            
            children_data[child_id]["tests"].append({
                "test_id": test["test_id"],
                "respondent_type": test["respondent_type"],
                "email": test["email"],
                "submitted": test.get("submitted", False),
                "created_at": test.get("created_at", "")
            })
        
        for child_id in children_data:
            review = reviews_collection.find_one({"child_id": child_id})
            if review and review.get("status") == "reviewed":
                children_data[child_id]["review_status"] = "reviewed"

        return list(children_data.values())
        
    except Exception as e:
        print(f"Error in get_child_tests_summary: {e}")
        return None

def get_test_results_for_user(child_id, email, role):
    """Get test results for a specific child (only if review is completed)"""
    try:
        review = reviews_collection.find_one({"child_id": child_id})
        if not review or review.get("status") != "reviewed":
            return None
            
        child_info = get_child_by_id(child_id)
        if not child_info:
            return None
            
        all_tests = list(tests_collection.find({"child_id": child_id}))
        
        user_test = None
        for test in all_tests:
            if test.get("email") == email and test.get("respondent_type") == role:
                user_test = test
                break
                
        if not user_test:
            return None
            
        return {
            "child_id": child_id,
            "child_name": child_info.get("name", "Unknown"),
            "test_id": user_test["test_id"],
            "user_score": user_test.get("scores", {}),
            "psychologist_review": review.get("psychologist_review", ""),
            "review_date": review.get("submitted_at", ""),
            "all_scores": review.get("scores", {}),
            "status": "completed"
        }
        
    except Exception as e:
        print(f"Error in get_test_results_for_user: {e}")
        return None

# ---------------------------- TEST MANAGEMENT FUNCTIONS ----------------------------
def get_tests_by_respondent(email, role):
    user_tests = list(tests_collection.find({
        "respondent_type": role,
        "email": email
    }))
    return user_tests

def create_test_entry(test_id, age, child_name, child_id, respondent_type, email):
    print("Inserting test_id into Mongo:", test_id)
    tests_collection.insert_one({
        "test_id": test_id,
        "age": age,
        "child_name": child_name,
        "child_id": child_id,
        "respondent_type": respondent_type,
        "email": email,
        "submitted": False,
        "confirm_options": [],
        "vector_responses": [],
        "scores": None,
        "created_at": datetime.utcnow()
    })

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
    """Generate and store score for a test"""
    from backend_api.score import calculate_score
    
    try:
        score_data = calculate_score(test_id)
        
        tests_collection.update_one(
            {"test_id": test_id},
            {"$set": {"scores": score_data}}
        )
        
        print(f"Score generated and stored for test {test_id}: {score_data}")
        return score_data
        
    except Exception as e:
        print(f"Error generating score for test {test_id}: {e}")
        raise e

def check_all_submitted(child_id):
    submitted_roles = tests_collection.find({
        "child_id": child_id,
        "submitted": True
    }).distinct("respondent_type")

    return all(role in submitted_roles for role in ["child", "parent", "teacher"])

def generate_ai_summary(all_tests, child_info):
    """Generate AI summary using LLM with proper prompt"""
    try:
        prompt = build_summary_prompt(all_tests, child_info)
        summary = query_llm(prompt)
        return summary
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        # Fallback to simple summary
        total_responses = sum(len(test.get("vector_responses", [])) for test in all_tests)
        avg_score = sum(test.get("scores", {}).get("total_score", 0) for test in all_tests) / len(all_tests)
        
        return f"""
Assessment Summary for {child_info.get('name', 'Child')} (Age: {child_info.get('age', 'Unknown')}):

• Total test responses analyzed: {total_responses}
• Average SDQ score across all respondents: {avg_score:.1f}/50
• Assessment completed by: {', '.join([test['respondent_type'].title() for test in all_tests])}

Based on the responses from child, parent, and teacher perspectives, this assessment provides insights into the child's behavioral and emotional wellbeing. The psychologist will review these findings and provide detailed recommendations.

Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()

def create_review_if_ready(test_id):
    """Create review document when all three parties have submitted"""
    test = tests_collection.find_one({"test_id": test_id})
    if not test:
        return False
        
    child_id = test["child_id"]

    if not check_all_submitted(child_id):
        print(f"Not all parties submitted for child {child_id}")
        return False

    existing = reviews_collection.find_one({"child_id": child_id})
    if existing:
        print(f"Review already exists for child {child_id}")
        return False

    all_tests = list(tests_collection.find({"child_id": child_id}))
    child_info = get_child_by_id(child_id)
    
    test_ids = {}
    scores = {}
    
    for test in all_tests:
        respondent_type = test["respondent_type"]
        test_ids[respondent_type] = test["test_id"]
        scores[respondent_type] = test.get("scores", {})
    
    ai_summary = generate_ai_summary(all_tests, child_info)

    review_doc = {
        "child_id": child_id,
        "child_test_id": test_ids.get("child", ""),
        "parent_test_id": test_ids.get("parent", ""),
        "teacher_test_id": test_ids.get("teacher", ""),
        "ai_generated_summary": ai_summary,
        "status": "pending",
        "reviewed_by": None,
        "psychologist_review": ai_summary,
        "scores": scores,
        "submitted_at": datetime.utcnow()
    }

    reviews_collection.insert_one(review_doc)
    print(f"Review created for child {child_id}")
    return True

def get_review_status(child_id):
    review = reviews_collection.find_one({"child_id": child_id})
    if not review:
        return {"status": "waiting", "message": "Review not generated yet."}

    return {
        "status": review["status"],
        "summary": review["psychologist_review"] if review["status"] == "reviewed" else None
    }

# ---------------------------- PSYCHOLOGIST FUNCTIONS ----------------------------
def get_pending_reviews():
    """Get all reviews pending psychologist review"""
    reviews = reviews_collection.find({"status": "pending"})
    result = []

    for review in reviews:
        child_info = get_child_by_id(review["child_id"])
        result.append({
            "child_id": review["child_id"],
            "name": child_info.get("name", "Unknown") if child_info else "Unknown",
            "date": review.get("submitted_at", "Unknown"),
            "screeningType": "SDQ",
            "status": "pending"
        })

    return result

def get_completed_reviews():
    """Get all completed psychologist reviews"""
    reviews = reviews_collection.find({"status": "reviewed"})
    result = []

    for review in reviews:
        child_info = get_child_by_id(review["child_id"])
        result.append({
            "child_id": review["child_id"],
            "name": child_info.get("name", "Unknown") if child_info else "Unknown",
            "date": review.get("reviewed_at", review.get("submitted_at", "Unknown")),
            "screeningType": "SDQ",
            "status": "reviewed"
        })

    return result

def get_full_review(child_id):
    """Get comprehensive test data for psychologist review with decoded chat history and questions"""
    review = reviews_collection.find_one({"child_id": child_id})
    if not review:
        raise Exception("Review not found.")

    all_tests = list(tests_collection.find({"child_id": child_id}))
    test_map = {t["respondent_type"]: t for t in all_tests}
    child_info = get_child_by_id(child_id)

    # Get questions for the child's age
    questions = []
    if child_info and child_info.get("age"):
        try:
            questions = get_questions_for_age(int(child_info["age"]))
        except (ValueError, TypeError):
            print(f"Invalid age for child {child_id}, using default questions")
            questions = get_questions_for_age(8)  # Default to middle age range

    # Process each test and attach vector responses with original text
    for respondent_type, test_data in test_map.items():
        test_id = test_data.get("test_id")
        if test_id:
            # Get vector responses from separate collection
            vector_docs = list(vector_responses_collection.find({"test_id": test_id}))
            text_map = {}
            
            for doc in vector_docs:
                q_index = doc.get("question_index")
                original_text = doc.get("original_text", [])
                if q_index is not None:
                    text_map[q_index] = original_text

            # Also check vector_responses in the test document itself
            test_vector_responses = test_data.get("vector_responses", [])
            for vr in test_vector_responses:
                q_index = vr.get("question_index")
                text = vr.get("text", "")
                if q_index is not None and text:
                    if q_index not in text_map:
                        text_map[q_index] = []
                    if isinstance(text, list):
                        text_map[q_index].extend(text)
                    else:
                        text_map[q_index].append(text)

            test_data["vector_responses_text"] = text_map

    return {
        "child_id": review["child_id"],
        "child_info": child_info,
        "questions": questions,  # Added questions list
        "test_ids": {
            "child": review.get("child_test_id", ""),
            "parent": review.get("parent_test_id", ""),
            "teacher": review.get("teacher_test_id", "")
        },
        "scores": review["scores"],
        "ai_summary": review["ai_generated_summary"],
        "status": review["status"],
        "psychologist_review": review["psychologist_review"],
        "tests": test_map
    }

def submit_review(child_id, psychologist_review, reviewer_id):
    """Submit psychologist review and mark as completed"""
    result = reviews_collection.update_one(
        {"child_id": child_id},
        {
            "$set": {
                "status": "reviewed",
                "psychologist_review": psychologist_review,
                "reviewed_by": reviewer_id,
                "reviewed_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise Exception("Review not found or could not be updated")
    
    print(f"Review submitted for child {child_id} by {reviewer_id}")

def get_final_review_for_user(child_id):
    """Get final review for end users (parent/teacher)"""
    review = reviews_collection.find_one({"child_id": child_id})
    if not review:
        raise Exception("No review found for this child.")

    if review["status"] != "reviewed":
        return {"status": "pending", "message": "Review not yet completed by psychologist."}

    return {
        "status": "reviewed",
        "summary": review["psychologist_review"]
    }

# ---------------------------- UTILITY FUNCTIONS ----------------------------
def find_existing_incomplete_test(child_id, respondent_type, email):
    """Find existing incomplete test for the same child, respondent type, and email"""
    existing_test = tests_collection.find_one({
        "child_id": child_id,
        "respondent_type": respondent_type,
        "email": email,
        "submitted": False
    })
    return existing_test

def create_or_resume_test(child_id, age, child_name, respondent_type, email):
    """Create new test or return existing incomplete test"""
    existing_test = find_existing_incomplete_test(child_id, respondent_type, email)
    
    if existing_test:
        print(f"Found existing incomplete test: {existing_test['test_id']}")
        return {
            "test_id": existing_test["test_id"],
            "is_new": False,
            "message": "Resuming your previous test..."
        }
    
    test_id = str(__import__('uuid').uuid4())
    print("Creating new test_id:", test_id)
    
    tests_collection.insert_one({
        "test_id": test_id,
        "age": age,
        "child_name": child_name,
        "child_id": child_id,
        "respondent_type": respondent_type,
        "email": email,
        "submitted": False,
        "confirm_options": [],
        "vector_responses": [],
        "scores": None,
        "created_at": datetime.utcnow()
    })
    
    return {
        "test_id": test_id,
        "is_new": True,
        "message": "Starting new test..."
    }
    
def get_test_by_id(test_id):
    """Get test data by test_id"""
    test = tests_collection.find_one({"test_id": test_id})
    if not test:
        raise Exception(f"Test with id {test_id} not found")
    return test

def upsert_review_and_generate_summary(test_id):
    """Update or create review with new summary based on all submitted tests"""
    test = get_test_by_id(test_id)
    if not test:
        raise Exception("Invalid test_id")

    child_id = test["child_id"]
    all_tests = list(tests_collection.find({"child_id": child_id, "submitted": True}))
    if not all_tests:
        print("No completed tests yet")
        return False

    child_info = get_child_by_id(child_id)
    if not child_info:
        print("Child info not found")
        return False

    review = reviews_collection.find_one({"child_id": child_id})

    test_ids = {}
    scores = {}
    for t in all_tests:
        test_ids[t["respondent_type"]] = t["test_id"]
        scores[t["respondent_type"]] = t.get("scores", {})

    ai_summary = generate_ai_summary(all_tests, child_info)

    if not review:
        reviews_collection.insert_one({
            "child_id": child_id,
            "child_test_id": test_ids.get("child", ""),
            "parent_test_id": test_ids.get("parent", ""),
            "teacher_test_id": test_ids.get("teacher", ""),
            "ai_generated_summary": ai_summary,
            "psychologist_review": ai_summary,
            "scores": scores,
            "status": "pending",
            "reviewed_by": None,
            "submitted_at": datetime.utcnow()
        })
        print(f"New review created for child {child_id}")
    else:
        reviews_collection.update_one(
            {"child_id": child_id},
            {
                "$set": {
                    "child_test_id": test_ids.get("child", ""),
                    "parent_test_id": test_ids.get("parent", ""),
                    "teacher_test_id": test_ids.get("teacher", ""),
                    "ai_generated_summary": ai_summary,
                    "psychologist_review": ai_summary,
                    "scores": scores,
                    "submitted_at": datetime.utcnow()
                }
            }
        )
        print(f"Review updated for child {child_id}")

    return True

def login_child_by_email(email):
    """Fetch child data using email"""
    return children_collection.find_one({"email": email})

def get_results_by_child_id(child_id: str, user_email: str, user_role: str):
    """Get completed review results for a specific child"""
    try:
        review = reviews_collection.find_one({"child_id": child_id})
        
        if not review:
            raise Exception("No review found for this child")
            
        if review.get("status") != "reviewed":
            raise Exception("Review not completed yet")

        user_test = tests_collection.find_one({
            "child_id": child_id,
            "email": user_email,
            "respondent_type": user_role
        })
        
        if not user_test:
            raise Exception("No test found for this user and child")
        
        child = children_collection.find_one({"child_id": child_id})
        child_name = child.get("name", "Unknown") if child else "Unknown"
        
        result = {
            "child_id": child_id,
            "child_name": child_name,
            "user_email": user_email,
            "user_role": user_role,
            "user_score": user_test.get("scores", {}),
            "review_date": review.get("reviewed_at", ""),
            "psychologist_review": review.get("psychologist_review", ""),
            "reviewed_by": review.get("reviewed_by", ""),
            "test_date": user_test.get("created_at", ""),
            "status": review.get("status")
        }
        
        return result
        
    except Exception as e:
        print(f"Error in get_results_by_child_id: {e}")
        raise e
    
def get_review_status_by_child_id(child_id: str):
    """Get review status directly from reviews collection"""
    try:
        review = reviews_collection.find_one({"child_id": child_id})
        if review:
            return review.get("status")
        return None
    except Exception as e:
        print(f"Error getting review status: {e}")
        return None

# ---------------------------- SCORING INTEGRATION ----------------------------
def get_category_score_for_review(test_data, category_indices):
    """Calculate category score for review display"""
    if not test_data or not test_data.get("scores", {}).get("subscale_scores"):
        return 0
    
    subscale_scores = test_data["scores"]["subscale_scores"]
    
    # Map category indices to subscale names
    EMOTIONAL = [2, 7, 12, 15, 23]
    CONDUCT = [4, 6, 11, 17, 21]
    HYPERACTIVITY = [1, 9, 14, 20, 24]
    PEER = [5, 10, 13, 18, 22]
    PROSOCIAL = [0, 3, 8, 16, 19]
    
    if category_indices == EMOTIONAL:
        return subscale_scores.get("emotional", 0)
    elif category_indices == CONDUCT:
        return subscale_scores.get("conduct", 0)
    elif category_indices == HYPERACTIVITY:
        return subscale_scores.get("hyperactivity", 0)
    elif category_indices == PEER:
        return subscale_scores.get("peer", 0)
    elif category_indices == PROSOCIAL:
        return subscale_scores.get("prosocial", 0)
    
    return 0