from fastapi import FastAPI
from backend_api import chat
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_api import review
app = FastAPI()

origins = [
    "http://localhost:3000",  # your frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],  # or specify ["GET", "POST", "OPTIONS"]
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat")
app.include_router(review.router)