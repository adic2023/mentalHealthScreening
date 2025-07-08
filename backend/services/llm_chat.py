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
