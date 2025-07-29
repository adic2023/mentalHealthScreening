# core/prompt_builder.py

from typing import List, Dict
from utils.intent_classifier import detect_user_intent

# --- Question banks omitted for brevity ---
QUESTIONS_2_TO_4 = [
    "Considerate of other people's feelings",
    "Restless, overactive, cannot stay still for long",
    "Often complains of headaches, stomach-aches or sickness",
    "Shares readily with other children, for example toys, treats, pencils",
    "Often loses temper",
    "Rather solitary, prefers to play alone",
    "Generally well behaved, usually does what adults request",
    "Many worries or often seems worried",
    "Helpful if someone is hurt, upset or feeling ill",
    "Constantly fidgeting or squirming",
    "Has at least one good friend",
    "Often fights with other children or bullies them",
    "Often unhappy, depressed or tearful",
    "Generally liked by other children",
    "Easily distracted, concentration wanders",
    "Nervous or clingy in new situations, easily loses confidence",
    "Kind to younger children",
    "Often argumentative with adults",
    "Picked on or bullied by other children",
    "Often offers to help others (parents, teachers, other children)",
    "Can stop and think things out before acting",
    "Can be spiteful to others",
    "Gets along better with adults than with other children",
    "Many fears, easily scared",
    "Good attention span, sees work through to the end"
]

QUESTIONS_4_TO_10 = [
    "Considerate of other people's feelings",
    "Restless, overactive, cannot stay still for long",
    "Often complains of headaches, stomach-aches or sickness",
    "Shares readily with other children, for example toys, treats, pencils",
    "Often loses temper",
    "Rather solitary, prefers to play alone",
    "Generally well behaved, usually does what adults request",
    "Many worries or often seems worried",
    "Helpful if someone is hurt, upset or feeling ill",
    "Constantly fidgeting or squirming",
    "Has at least one good friend",
    "Often fights with other children or bullies them",
    "Often unhappy, depressed or tearful",
    "Generally liked by other children",
    "Easily distracted, concentration wanders",
    "Nervous or clingy in new situations, easily loses confidence",
    "Kind to younger children",
    "Often lies or cheats",
    "Picked on or bullied by other children",
    "Often offers to help others (parents, teachers, other children)",
    "Thinks things out before acting",
    "Steals from home, school or elsewhere",
    "Gets along better with adults than with other children",
    "Many fears, easily scared",
    "Good attention span, sees work through to the end"
]

QUESTIONS_11_TO_17 = [
    "Considerate of other people's feelings",
    "Restless, overactive, cannot stay still for long",
    "Often complains of headaches, stomach-aches or sickness",
    "Shares readily with other youth, for example books, games, food",
    "Often loses temper",
    "Would rather be alone than with other youth",
    "Generally well behaved, usually does what adults request",
    "Many worries or often seems worried",
    "Helpful if someone is hurt, upset or feeling ill",
    "Constantly fidgeting or squirming",
    "Has at least one good friend",
    "Often fights with other youth or bullies them",
    "Often unhappy, depressed or tearful",
    "Generally liked by other youth",
    "Easily distracted, concentration wanders",
    "Nervous in new situations, easily loses confidence",
    "Kind to younger children",
    "Often lies or cheats",
    "Picked on or bullied by other youth",
    "Often offers to help others (parents, teachers, children)",
    "Thinks things out before acting",
    "Steals from home, school or elsewhere",
    "Gets along better with adults than with other youth",
    "Many fears, easily scared",
    "Good attention span, sees work through to the end"
]

def get_questions_for_age(age: int) -> List[str]:
    if 2 <= age <= 4:
        return QUESTIONS_2_TO_4
    elif 5 <= age <= 10:
        return QUESTIONS_4_TO_10
    elif 11 <= age <= 17:
        return QUESTIONS_11_TO_17
    else:
        raise ValueError("Unsupported age group")

def convert_to_first_person(question: str) -> str:
    if question.lower().startswith("often "):
        return "do you " + question[6:].lower() + "?"
    elif question.lower().startswith("has "):
        return "do you have " + question[4:].lower() + "?"
    elif question.lower().startswith("gets "):
        return "do you get " + question[5:].lower() + "?"
    elif question.lower().startswith("steals "):
        return "do you steal " + question[7:].lower() + "?"
    elif question.lower().startswith("shares "):
        return "do you share " + question[7:].lower() + "?"
    return f"are you {question.lower()}?"

def format_question(question: str, name: str, respondent_type: str) -> str:
    if respondent_type == "child":
        return f"How often {convert_to_first_person(question)}"
    else:
        if question.startswith("Often "):
            return f"How often does {name} {question[6:].lower()}?"
        elif question.startswith("Has "):
            return f"Does {name} have {question[4:].lower()}?"
        elif question.startswith("Gets "):
            return f"Does {name} get {question[5:].lower()}?"
        elif question.startswith("Steals "):
            return f"Does {name} steal {question[7:].lower()}?"
        elif question.startswith("Shares "):
            return f"Does {name} share {question[7:].lower()}?"
        return f"Is {name} {question.lower()}?"

def build_question_prompt(question: str, name: str, respondent_type: str) -> str:
    q = format_question(question, name, respondent_type)
    return f"{q}\nOptions: Not True / Somewhat True / Certainly True"

def build_system_instruction(child_name: str, age: int, respondent_type: str) -> str:
    if respondent_type == "child":
        role_line = f"You're a warm assistant helping {child_name}, a {age}-year-old child."
    else:
        role_line = f"You're a helpful assistant asking a parent/teacher about {child_name}, a {age}-year-old child."

    return f"""
You are conducting a behavioral questionnaire (SDQ).
{role_line}

Rules:
- NEVER write 'User:', 'Assistant:', or simulate users.
- NEVER assume what the user says next.
- NEVER generate responses on the user's behalf.
- You must only respond as yourself.

Response style:
- Respond in 1–2 sentences in a natural, warm tone.
- Interpret the user's last answer and suggest: Not True / Somewhat True / Certainly True.
- End every message with: "Does that sound right?" and wait for confirmation.

Mapping rules:
- 'Never', 'rarely', 'hardly ever' → Not True
- 'Sometimes', 'occasionally', 'now and then' → Somewhat True
- 'Always', 'very often', 'frequently' → Certainly True

Examples:
- "Got it – sounds like 'Somewhat True'. Does that sound right?"
- "Right, they always do this – I'd say 'Certainly True'. Does that sound right?"
"""

def build_analysis_prompt(
    age: int,
    question_index: int,
    chat_history: List[Dict[str, str]],
    child_name: str,
    respondent_type: str
) -> str:
    system_instruction = build_system_instruction(child_name, age, respondent_type)
    messages = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
    question_text = format_question(get_questions_for_age(age)[question_index], child_name, respondent_type)

    return f"""
System: {system_instruction.strip()}

Assistant: Let's look at the following question: "{question_text}"
{messages}

Now based on the user's last response, what would you say?
Give a brief explanation and end with: "Does that sound right?"
"""

def build_explanation_prompt(question: str, name: str, respondent_type: str) -> str:
    formatted = format_question(question, name, respondent_type)
    who = "child" if respondent_type == "child" else "parent or teacher"
    return (
        f"A {who} didn't understand this question: '{formatted}'\n"
        f"Explain in 1–2 friendly sentences what this behavior would look like in real life. "
        f"Use concrete, everyday examples. Avoid repeating the question directly."
    )

def extract_option_from_llm_response(llm_response: str) -> str:
    response_lower = llm_response.lower()
    if "not true" in response_lower:
        return "Not True"
    elif "certainly true" in response_lower:
        return "Certainly True"
    elif "somewhat true" in response_lower:
        return "Somewhat True"
    elif any(x in response_lower for x in ["never", "rarely", "hardly ever", "no", "not really"]):
        return "Not True"
    elif any(x in response_lower for x in ["always", "frequently", "constantly", "every time"]):
        return "Certainly True"
    elif any(x in response_lower for x in ["sometimes", "occasionally", "in between"]):
        return "Somewhat True"
    return "Somewhat True"

def build_summary_prompt(all_tests: List[Dict], child_info: Dict) -> str:
    """Construct a prompt summarizing the child's behavioral test results from multiple perspectives."""
    name = child_info.get("name", "the child")
    age = child_info.get("age", "Unknown")
    intro = f"You are a psychologist analyzing SDQ test results for {name}, a {age}-year-old child."
    
    respondent_insights = []
    for test in all_tests:
        role = test["respondent_type"].capitalize()
        score = test.get("scores", {}).get("total_score", "N/A")
        responses = test.get("confirm_options", [])
        answer_summary = ", ".join([f"{r['question']} -> {r['selected_option']}" for r in responses[:5]])  # Limit to first 5
        
        respondent_insights.append(f"{role}'s interpretation:\n- SDQ Score: {score}\n- Sample answers: {answer_summary}")

    joined = "\n\n".join(respondent_insights)
    
    return f"""{intro}

{joined}

Now generate a professional psychologist-style summary capturing insights, behavioral patterns, and emotional well-being.
Keep it formal, insightful, and actionable."""
