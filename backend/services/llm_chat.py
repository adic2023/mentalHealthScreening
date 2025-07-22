import requests
import os

def query_llm(prompt: str) -> str:
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": "Qwen2-7B-Instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


# import requests

# def query_llm(prompt: str, history: list = None, system_instruction: str = None) -> str:
#     # Default values if not provided
#     history = history or []
#     system_instruction = system_instruction or "You are a helpful assistant."

#     messages = [{"role": "system", "content": system_instruction}]

#     # Add previous chat history
#     messages += history

#     # Add the latest user prompt
#     messages.append({"role": "user", "content": prompt})

#     response = requests.post(
#         "http://localhost:1234/v1/chat/completions",
#         headers={"Content-Type": "application/json"},
#         json={
#             "model": "Qwen2-7B-Instruct",
#             "messages": messages,
#             "temperature": 0.7
#         }
#     )
#     response.raise_for_status()
#     return response.json()['choices'][0]['message']['content'].strip()
