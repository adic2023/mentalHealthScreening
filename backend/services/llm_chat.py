# services/llm_chat.py

import os
import requests
from dotenv import load_dotenv
load_dotenv()


LLM_BACKEND = os.getenv("LLM_BACKEND")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

def query_llm(prompt: str) -> str:
    if LLM_BACKEND == "gemini":
        return query_gemini(prompt)
    elif LLM_BACKEND == "qwen":
        return query_qwen(prompt)
    else:
        raise ValueError(f"Unsupported LLM_BACKEND: {LLM_BACKEND}")

def query_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]