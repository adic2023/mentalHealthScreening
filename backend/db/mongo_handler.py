# db/mongo_handler.py
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["sdq_test_db"]

tests_collection = db["tests"]
children_collection = db["children"]
users_collection = db["users"]
reviews_collection = db["reviews"]  # Explicit reference

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
    return children_collection.find_one({"code": code})

def get_child_by_id(child_id):
    """Get child data by child_id"""
    return children_collection.find_one({"child_id": child_id})

def get_child_code(child_id):
    """Get sharing code for a child"""
    child = children_collection.find_one({"child_id": child_id})
    return child.get("code") if child else None

# ---------------------------- UPDATED DASHBOARD FUNCTIONS ----------------------------
def get_child_tests_summary(email, role):
    """Get dashboard summary for parent/teacher - groups tests by child"""
    try:
        # Find all tests by this user
        user_tests = list(tests_collection.find({
            "email": email,
            "respondent_type": role
        }))
        
        if not user_tests:
            return None
            
        # Group by child_id
        children_data = {}
        
        for test in user_tests:
            child_id = test["child_id"]
            
            if child_id not in children_data:
                # Get child info
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
        
        # Check review status for each child
        for child_id in children_data:
            review = reviews_collection.find_one({"child_id": child_id})
            if review and review.get("status") == "reviewed":
                children_data[child_id]["review_status"] = "completed"
        
        return list(children_data.values())
        
    except Exception as e:
        print(f"Error in get_child_tests_summary: {e}")
        return None

def get_test_results_for_user(child_id, email, role):
    """Get test results for a specific child (only if review is completed)"""
    try:
        # Check if review is completed
        review = reviews_collection.find_one({"child_id": child_id})
        if not review or review.get("status") != "reviewed":
            return None
            
        # Get child info
        child_info = get_child_by_id(child_id)
        if not child_info:
            return None
            
        # Get all tests for this child
        all_tests = list(tests_collection.find({"child_id": child_id}))
        
        # Get user's specific test
        user_test = None
        for test in all_tests:
            if test.get("email") == email and test.get("respondent_type") == role:
                user_test = test
                break
                
        if not user_test:
            return None
            
        # Return results with psychologist review
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

# ---------------------------- EXISTING FUNCTIONS (KEPT UNCHANGED) ----------------------------
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
        "scores": None,  # Added scores field
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
        
        # Store the score in the test document
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
    """Generate AI summary from test data and chat responses"""
    # Simple placeholder - you can enhance this with actual AI
    total_responses = sum(len(test.get("vector_responses", [])) for test in all_tests)
    avg_score = sum(test.get("scores", {}).get("total_score", 0) for test in all_tests) / len(all_tests)
    
    summary = f"""
    Assessment Summary for {child_info.get('name', 'Child')} (Age: {child_info.get('age', 'Unknown')}):
    
    • Total test responses analyzed: {total_responses}
    • Average SDQ score across all respondents: {avg_score:.1f}/50
    • Assessment completed by: {', '.join([test['respondent_type'].title() for test in all_tests])}
    
    Based on the responses from child, parent, and teacher perspectives, this assessment provides insights into the child's behavioral and emotional wellbeing. The psychologist will review these findings and provide detailed recommendations.
    
    Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
    """
    
    return summary.strip()

def create_review_if_ready(test_id):
    """Create review document when all three parties have submitted"""
    test = tests_collection.find_one({"test_id": test_id})
    if not test:
        return False
        
    child_id = test["child_id"]

    # Check if all three parties have submitted
    if not check_all_submitted(child_id):
        print(f"Not all parties submitted for child {child_id}")
        return False

    # Check if review already exists
    existing = reviews_collection.find_one({"child_id": child_id})
    if existing:
        print(f"Review already exists for child {child_id}")
        return False

    # Get all tests for this child
    all_tests = list(tests_collection.find({"child_id": child_id}))
    
    # Get child information
    child_info = get_child_by_id(child_id)
    
    # Create test_ids mapping
    test_ids = {}
    scores = {}
    
    for test in all_tests:
        respondent_type = test["respondent_type"]
        test_ids[respondent_type] = test["test_id"]
        scores[respondent_type] = test.get("scores", {})
    
    # Generate AI summary
    ai_summary = generate_ai_summary(all_tests, child_info)

    # Create review document
    review_doc = {
        "child_id": child_id,
        "child_test_id": test_ids.get("child", ""),
        "parent_test_id": test_ids.get("parent", ""),
        "teacher_test_id": test_ids.get("teacher", ""),
        "ai_generated_summary": ai_summary,
        "status": "pending",  # pending -> reviewed
        "reviewed_by": None,  # Will be set when psychologist reviews
        "psychologist_review": ai_summary,  # Initially same as AI summary
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
            "child_name": child_info.get("name", "Unknown") if child_info else "Unknown",
            "submitted_at": review["submitted_at"]
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
            "child_name": child_info.get("name", "Unknown") if child_info else "Unknown",
            "reviewed_by": review["reviewed_by"],
            "reviewed_at": review.get("reviewed_at", review["submitted_at"])
        })
    
    return result

def get_full_review(child_id):
    """Get comprehensive test data for psychologist review"""
    review = reviews_collection.find_one({"child_id": child_id})
    if not review:
        raise Exception("Review not found.")

    # Get all test data
    all_tests = list(tests_collection.find({"child_id": child_id}))
    test_map = {t["respondent_type"]: t for t in all_tests}
    
    # Get child info
    child_info = get_child_by_id(child_id)

    return {
        "child_id": review["child_id"],
        "child_info": child_info,
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
    # Check for existing incomplete test
    existing_test = find_existing_incomplete_test(child_id, respondent_type, email)
    
    if existing_test:
        print(f"Found existing incomplete test: {existing_test['test_id']}")
        return {
            "test_id": existing_test["test_id"],
            "is_new": False,
            "message": "Resuming your previous test..."
        }
    
    # Create new test if none exists
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
        "scores": None,  # Added scores field
        "created_at": datetime.utcnow()
    })
    
    return {
        "test_id": test_id,
        "is_new": True,
        "message": "Starting new test..."
    }
    
def get_test_by_id(test_id):
    """Get test data by test_id - needed for score calculation"""
    test = tests_collection.find_one({"test_id": test_id})
    if not test:
        raise Exception(f"Test with id {test_id} not found")
    return test