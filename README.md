# mentalHealthScreening

```
sdq-chat-app/
│
├── backend/                           # FastAPI backend
│   ├── main.py                        # Entrypoint
│   ├── api/
│   │   ├── chat.py                    # /chat/start and /chat/answer endpoints
│   │   └── score.py                   # /score/test endpoint
│   ├── core/
│   │   ├── prompt_builder.py          # Builds prompts based on age/context
│   │   └── context_tracker.py         # Maintains super context logic
│   ├── db/
│   │   ├── mongo_handler.py           # MongoDB ops for summary/options
│   │   └── vector_store.py            # Vector DB handler for conversation memory
│   ├── services/
│   │   ├── llm_chat.py                # Handles SDQ question-answering loop
│   │   └── llm_score.py               # Handles scoring logic (you)
│   └── models.py                      # Pydantic models and schemas
│
├── frontend/                          # React single-page app
│   ├── index.html
│   └── App.jsx                        # Age input, chat window, option confirm
│
├── .env                               # Keys and secrets
└── README.md
```

![WhatsApp Image 2025-07-03 at 12 27 59_165e4df2](https://github.com/user-attachments/assets/5d7bb8b0-8fad-441b-932c-deb735dee4a0)

