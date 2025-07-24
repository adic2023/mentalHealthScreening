# prompt_builder.py

from typing import List, Dict

# Static SDQ question banks by age group
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
    """Convert third person question to first person for child respondents"""
    # Dictionary of common conversions
    conversions = {
        "Considerate of other people's feelings": "considerate of other people's feelings",
        "Restless, overactive, cannot stay still for long": "restless, overactive, cannot stay still for long",
        "Often complains of headaches, stomach-aches or sickness": "often complain of headaches, stomach-aches or sickness",
        "Shares readily with other children, for example toys, treats, pencils": "share readily with other children, for example toys, treats, pencils",
        "Shares readily with other youth, for example books, games, food": "share readily with other youth, for example books, games, food",
        "Often loses temper": "often lose your temper",
        "Rather solitary, prefers to play alone": "rather solitary, prefer to play alone",
        "Would rather be alone than with other youth": "would rather be alone than with other youth",
        "Generally well behaved, usually does what adults request": "generally well behaved, usually do what adults request",
        "Many worries or often seems worried": "have many worries or often seem worried",
        "Helpful if someone is hurt, upset or feeling ill": "helpful if someone is hurt, upset or feeling ill",
        "Constantly fidgeting or squirming": "constantly fidgeting or squirming",
        "Has at least one good friend": "have at least one good friend",
        "Often fights with other children or bullies them": "often fight with other children or bully them",
        "Often fights with other youth or bullies them": "often fight with other youth or bully them",
        "Often unhappy, depressed or tearful": "often unhappy, depressed or tearful",
        "Generally liked by other children": "generally liked by other children",
        "Generally liked by other youth": "generally liked by other youth",
        "Easily distracted, concentration wanders": "easily distracted, concentration wanders",
        "Nervous or clingy in new situations, easily loses confidence": "nervous or clingy in new situations, easily lose confidence",
        "Nervous in new situations, easily loses confidence": "nervous in new situations, easily lose confidence",
        "Kind to younger children": "kind to younger children",
        "Often argumentative with adults": "often argumentative with adults",
        "Often lies or cheats": "often lie or cheat",
        "Picked on or bullied by other children": "picked on or bullied by other children",
        "Picked on or bullied by other youth": "picked on or bullied by other youth",
        "Often offers to help others (parents, teachers, other children)": "often offer to help others (parents, teachers, other children)",
        "Often offers to help others (parents, teachers, children)": "often offer to help others (parents, teachers, children)",
        "Can stop and think things out before acting": "can stop and think things out before acting",
        "Thinks things out before acting": "think things out before acting",
        "Can be spiteful to others": "can be spiteful to others",
        "Steals from home, school or elsewhere": "steal from home, school or elsewhere",
        "Gets along better with adults than with other children": "get along better with adults than with other children",
        "Gets along better with adults than with other youth": "get along better with adults than with other youth",
        "Many fears, easily scared": "have many fears, easily scared",
        "Good attention span, sees work through to the end": "have a good attention span, see work through to the end"
    }
    
    # Return the conversion if it exists
    return conversions.get(question, question.lower())

def format_question_for_grammar(question: str, child_name: str, respondent_type: str = "parent") -> str:
    """Format question with proper grammar based on respondent type"""
    if respondent_type == "child":
        first_person_question = convert_to_first_person(question)
        return f"How often are you {first_person_question}?"
    else:
        # Fix grammar for third person questions
        if question.startswith("Often "):
            # "Often loses temper" -> "How often does {name} lose his/her temper?"
            verb_phrase = question[6:]  # Remove "Often "
            if "loses" in verb_phrase:
                verb_phrase = verb_phrase.replace("loses", "lose")
            elif "complains" in verb_phrase:
                verb_phrase = verb_phrase.replace("complains", "complain")
            elif "offers" in verb_phrase:
                verb_phrase = verb_phrase.replace("offers", "offer")
            elif "lies" in verb_phrase:
                verb_phrase = verb_phrase.replace("lies", "lie")
            elif "fights" in verb_phrase:
                verb_phrase = verb_phrase.replace("fights", "fight")
            return f"How often does {child_name} {verb_phrase.lower()}?"
        elif question.startswith("Has "):
            # "Has at least one good friend" -> "Does {name} have at least one good friend?"
            verb_phrase = question[4:]  # Remove "Has "
            return f"Does {child_name} have {verb_phrase.lower()}?"
        elif question.startswith("Gets "):
            # "Gets along better..." -> "Does {name} get along better..."
            verb_phrase = question[5:]  # Remove "Gets "
            return f"Does {child_name} get {verb_phrase.lower()}?"
        elif question.startswith("Thinks "):
            # "Thinks things out..." -> "Does {name} think things out..."
            verb_phrase = question[7:]  # Remove "Thinks "
            return f"Does {child_name} think {verb_phrase.lower()}?"
        elif question.startswith("Steals "):
            # "Steals from..." -> "Does {name} steal from..."
            verb_phrase = question[7:]  # Remove "Steals "
            return f"Does {child_name} steal {verb_phrase.lower()}?"
        elif question.startswith("Shares "):
            # "Shares readily..." -> "Does {name} share readily..."
            verb_phrase = question[7:]  # Remove "Shares "
            return f"Does {child_name} share {verb_phrase.lower()}?"
        else:
            # For other patterns, use "Is {name}..."
            return f"Is {child_name} {question.lower()}?"

def personalize_question(question: str, name: str, respondent_type: str = "parent") -> str:
    """Personalize question based on who is responding"""
    formatted_question = format_question_for_grammar(question, name, respondent_type)
    return f"{formatted_question}\nOptions: Not True / Somewhat True / Certainly True"

def build_prompt(
    age: int,
    question_index: int,
    chat_history: list,
    child_name: str = "the child",
    respondent_type: str = "parent",
    is_first: bool = False,
    is_analysis: bool = False
) -> str:
    questions = get_questions_for_age(age)
    if question_index < 0 or question_index >= len(questions):
        raise ValueError("Invalid question index.")

    current_question = questions[question_index]

    # Adjust system instruction based on respondent type
    if respondent_type == "child":
        system_instruction = (
            f"You are a friendly helper conducting a behavioral questionnaire with {child_name}, a {age}-year-old. "
            "Listen to what they say about themselves and naturally interpret their response into one of: "
            "'Not True', 'Somewhat True', or 'Certainly True'. "
        )
    else:
        system_instruction = (
            f"You are a friendly helper conducting a behavioral questionnaire about {child_name}, a {age}-year-old. "
            "Listen to what the parent/caregiver says and naturally interpret their response into one of: "
            "'Not True', 'Somewhat True', or 'Certainly True'. "
        )
    
    system_instruction += (
        "CRITICAL: Only respond as the assistant. Never generate fake user messages or conversations. "
        "Never write 'User:' or 'Assistant:' in your response.\n"
        
        "IMPORTANT - When user gives a clear answer (Not True/Somewhat True/Certainly True):\n"
        "1. Accept their answer immediately\n"
        "2. Acknowledge it briefly and move on\n"
        "3. Don't keep asking the same question\n"
        "4. Don't provide explanations unless they seem confused\n"
        
        "Sound natural and conversational:\n"
        "1. Respond like a warm, understanding person - not a robot\n"
        "2. Acknowledge what they said in natural language\n"
        "3. Don't use phrases like 'maps to' or 'I'll mark this as'\n"
        "4. Use everyday language: 'Got it', 'I understand', 'That sounds like'\n"
        "5. Be brief but friendly - 1-2 sentences max\n"
        
        "Response style examples:\n"
    )
    
    if respondent_type == "child":
        system_instruction += (
            "- 'Got it - so you're considerate sometimes but not always. That sounds like \"Somewhat True\" to me.'\n"
            "- 'I understand - you rarely do this. I'd say \"Not True\" then.'\n"
            "- 'Right, so you do this quite often. That would be \"Certainly True\".'\n"
            "- When they say 'Somewhat True': 'Perfect! That makes sense.'\n"
            "- When they say 'Not True': 'Got it, thanks!'\n"
        )
    else:
        system_instruction += (
            f"- 'Got it - so {child_name} is considerate sometimes but not always. That sounds like \"Somewhat True\" to me.'\n"
            f"- 'I understand - {child_name} rarely does this. I'd say \"Not True\" then.'\n"
            f"- 'Right, so {child_name} does this quite often. That would be \"Certainly True\".'\n"
            f"- When they say 'Somewhat True': 'Perfect! That makes sense.'\n"
            f"- When they say 'Not True': 'Got it, thanks!'\n"
        )
    
    system_instruction += (
        "When the user gives a direct answer (Not True/Somewhat True/Certainly True), "
        "simply acknowledge it and confirm. Don't keep re-asking or explaining. "
        "Only ask 'Does that sound right?' if you're interpreting their descriptive answer."
    )

    formatted_history = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
    ])

    if is_first:
        welcome_message = (
            "Hello! I'm here to guide you through a short behavioral questionnaire. "
            "Shall we begin? Type 'yes' to start."
        )
        return f"System: {system_instruction}\n{formatted_history}\nAssistant: {welcome_message}"

    if is_analysis:
        formatted_question = format_question_for_grammar(current_question, child_name, respondent_type)
        question_text = f"Current Question: {formatted_question}\n\n"
            
        return (
            f"{system_instruction}\n"
            f"{question_text}"
            f"{formatted_history}\n\n"
            "Look at what the user just said and interpret it naturally. Respond in a warm, "
            "conversational way that shows you understand them. Keep it brief and friendly. "
            "Only provide explanations if they seem confused."
        )

    question_prompt = personalize_question(current_question, child_name, respondent_type)
    return f"System: {system_instruction}\n{formatted_history}\nAssistant: {question_prompt}"

def user_seems_confused(user_input: str) -> bool:
    """Check if user seems confused and needs explanation"""
    user_lower = user_input.lower().strip()
    
    # If user gives a direct answer, they're not confused
    direct_answers = ["not true", "somewhat true", "certainly true", "yes", "no"]
    if any(answer in user_lower for answer in direct_answers):
        return False
    
    # Check for confusion indicators
    confusion_keywords = [
        "didn't understand", "didnt understand", "dont understand", "don't understand",
        "what does it mean", "what do you mean", "not clear", "can you explain", 
        "i'm confused", "im confused", "confused", "unclear", "what", "huh", "?",
        "explain", "clarify", "help me understand"
    ]
    return any(kw in user_lower for kw in confusion_keywords)

def build_explanation_prompt(question: str, child_name: str = "the child", respondent_type: str = "parent") -> str:
    """Build explanation prompt only when user is confused"""
    formatted_question = format_question_for_grammar(question, child_name, respondent_type)
    
    if respondent_type == "child":
        explanation_text = f"A child doesn't understand this question: '{formatted_question}'\n\n"
    else:
        explanation_text = f"A parent doesn't understand this question: '{formatted_question}'\n\n"
    
    return (
        f"{explanation_text}"
        "Explain what this behavior actually looks like in real life with concrete examples. "
        "Don't repeat the question - help them understand what to look for. "
        "Keep it to 1-2 simple sentences."
    )

def extract_option_from_llm_response(llm_response: str) -> str:
    """Extract the selected SDQ option from LLM response"""
    response_lower = llm_response.lower()
    
    # Look for explicit option statements
    if "not true" in response_lower:
        return "Not True"
    elif "certainly true" in response_lower:
        return "Certainly True"
    elif "somewhat true" in response_lower:
        return "Somewhat True"
    
    # Fallback - look for keywords that suggest intensity
    if any(word in response_lower for word in ["never", "rarely", "not really", "no"]):
        return "Not True"
    elif any(word in response_lower for word in ["always", "very", "definitely", "constantly", "often"]):
        return "Certainly True"
    else:
        return "Somewhat True"  # Default for ambiguous cases