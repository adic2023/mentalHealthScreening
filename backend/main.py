from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llm_wrapper import LMStudioChat  # import your class
import requests

app = FastAPI()
chat = LMStudioChat()

# Enable CORS if frontend is on a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FormData(BaseModel):
    response: str

@app.post("/submit")
async def submit(data: FormData):
    user_input = data.response
    llm_reply = chat.ask(user_input)

    # External GET request, edit this to GET the "true, somewhat true, or not true"
    get_response = requests.get(f"http://localhost:8000/check?query={user_input}") 
    if get_response.status_code == 200:
        stored_answer = get_response.json().get("stored_answer", "")
    else:
        stored_answer = "No stored answer found."

    preset = f"Previous answer: {stored_answer}"

    return {
        # the llm will respond with an acknowledgement of what it received (or however we tell it to respond), 
        # and then it will send the preset response that asks for correction. 
        # need to figure out how we prompt for next question though
        # I could also put the preset response first but then llm will respond before user picks 
        "llm_reply": llm_reply,
        "preset_reply": preset
    }