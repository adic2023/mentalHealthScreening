from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_api import chat, review, auth, test, child  # ← Added test and child imports

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
app.include_router(auth.router, prefix="")
app.include_router(test.router, prefix="")  # ← Added test router registration
app.include_router(child.router, prefix="")  # ← Added child router registration