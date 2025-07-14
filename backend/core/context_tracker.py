def update_super_context(current_context: dict, new_message: str)->dict:
    updated =current_context.copy()
    updated["last_user_message"] =new_message
    return updated

def extract_context(chat_history):
    return {
        "user_mentions":[msg["content"] for msg in chat_history if msg["role"]=="user"],
        "assistant_suggestions":[msg["content"] for msg in chat_history if msg["role"]=="assistant"]
    }
    
    
'''
add this in chat.py at top:

from core.context_tracker import extract_context, update_super_context

inside respond after
questions = get_questions_for_age(req.age)
add:
# Extract conversational context
context = extract_context(req.chat_history)
print("Context Tracker Extracted:", context)

# Update (dummy) super context
super_context = update_super_context({}, req.chat_history[-1]["content"] if req.chat_history else "")
print("Updated Super Context:", super_context)

'''