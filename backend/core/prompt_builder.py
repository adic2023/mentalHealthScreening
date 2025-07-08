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
    "Often complains of headaches, stomach-aches or sickness Shares readily with other youth, for example books, games, food",
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

def build_prompt(age: int, question_index: int, chat_history: List[Dict], child_name: str = "the child", is_first: bool = False, is_analysis: bool = False) -> str:
    questions = get_questions_for_age(age)
    if question_index < 0 or question_index >= len(questions):
        raise ValueError("Invalid question index.")

    current_question = questions[question_index]

    system_instruction = (
        "You are a mental health assistant helping assess a child using the SDQ test. "
        f"The child is {age} years old. Ask one question at a time and listen to the user's input carefully. "
        "Then politely interpret their input into one of these three categories: 'Not True', 'Somewhat True', 'Certainly True'."
    )

    formatted_history = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
    ])

    if is_first:
        welcome_message = (
            "Hello! I'm here to guide you through a short questionnaire to help assess your child's behavior. "
            "This will only take a few minutes. Shall we begin the test? Please reply with 'Yes' to start."
        )
        return f"System: {system_instruction}\n{formatted_history}\nAssistant: {welcome_message}"

    if is_analysis:
        # Use for interpreting user views into a choice
        return (
            f"{system_instruction}\n"
            f"Current Question: '{current_question}'\n\n"
            f"{formatted_history}\n\n"
            f"Based on the user's input, select the most appropriate option:\n"
            f"Choices: ['Not True', 'Somewhat True', 'Certainly True'].\n"
            f"Reply ONLY with the best matching option and a short clarification like 'So you mean...?'"
        )

    # Normal question flow
    next_question = f"How often is {child_name} {current_question.lower()}?\nOptions: ['Not True', 'Somewhat True', 'Certainly True']"
    return f"System: {system_instruction}\n{formatted_history}\nAssistant: {next_question}"


def get_questions_for_age(age: int) -> List[str]:
    if 2 <= age <= 4:
        return QUESTIONS_2_TO_4
    elif 5 <= age <= 10:
        return QUESTIONS_4_TO_10
    elif 11 <= age <= 17:
        return QUESTIONS_11_TO_17
    else:
        raise ValueError("Unsupported age group")