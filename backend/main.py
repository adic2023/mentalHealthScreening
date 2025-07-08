from fastapi import FastAPI
from api import chat

app = FastAPI()

app.include_router(chat.router, prefix="/chat")
