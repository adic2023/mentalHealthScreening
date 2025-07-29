# core/intent_classifier.py

from services.llm_chat import query_llm
from typing import List, Dict

INTENT_LABELS = [
    "direct_answer",
    "confirmation",
    "correction",
    "confused",
    "asking_question",
    "sharing_experience",
    "unclear"
]

def detect_user_intent(chat_history: List[Dict[str, str]]) -> str:
    """
    Classifies what the user is doing in the latest message.
    Returns one of: direct_answer, confirmation, correction, confused, asking_question, sharing_experience, unclear
    """
    prompt = build_intent_prompt(chat_history)
    raw_response = query_llm(prompt).strip().lower()

    for label in INTENT_LABELS:
        if label in raw_response:
            return label
    return "unclear"

def build_intent_prompt(chat_history: List[Dict[str, str]]) -> str:
    last_user_msg = chat_history[-1]["content"]
    formatted_history = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history[-4:]
    ])

    return f"""
You are an intent classification expert.

Your job is to analyze the user's **latest message** in the context of their ongoing conversation with the assistant. You must classify their intent as one of the following:

- **direct_answer** → A clear choice like "Not True", "Somewhat True", or "Certainly True"
- **confirmation** → The user agrees with the assistant's suggestion or confirms a choice
- **correction** → The user is pushing back, suggesting a different answer, or clarifying they disagree
- **confused** → The user asks for clarification, expresses uncertainty or misunderstanding
- **asking_question** → The user is asking something about the question itself
- **sharing_experience** → The user shares a real-life story, behavior, or context
- **unclear** → The intent is ambiguous

Do not assume the user agrees unless they clearly confirm. If the user **adds new information** or pushes back slightly (e.g. says "but", "actually", or offers more context), label it as `correction`.

Here is the conversation:
{formatted_history}

User's latest message: "{last_user_msg}"

What is the user's intent? Reply with just the label (e.g., correction).
"""