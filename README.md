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


# SDQ AI Mental Health App – API Documentation

## 🔧 API Endpoints

---

### 1. `POST /chat/start`
**Purpose**: Initializes a new test session for a child based on age.

**Input**:
```json
{
  "age": number
}
```

**Output**:
```json
{
  "test_id": string,
  "question_id": string,
  "message": string
}
```

**Backend Logic**:
- Generates a dynamic prompt using age-based SDQ template.
- Stores initial test metadata in **MongoDB**.
- Prepares context for upcoming conversation.

**Handled By**:  
- Prompt structure: **Yatin**  
- API + frontend call: **Adi**

---

### 2. `POST /chat/respond`
**Purpose**: User responds to a question — continues the conversational flow.

**Input**:
```json
{
  "message": string,
  "test_id": string,
  "question_id": string
}
```

**Output**:
```json
{
  "message": string,
  "conversation_id": string,
  "next_state": string
}
```

**Backend Logic**:
- Passes message into LLM with super-context.
- Embeds and stores full chat turn in **VectorDB**.

**Handled By**:  
- VectorDB logic + LLM prompt handling: **Ansh**  
- Prompt structure: **Yatin**

---

### 3. `POST /chat/confirm-option`
**Purpose**: User confirms/choses final SDQ answer.

**Input**:
```json
{
  "test_id": string,
  "question_id": string,
  "option": string
}
```

**Output**:
```json
{
  "status": "saved",
  "next_question_id": string,
  "next_message": string
}
```

**Backend Logic**:
- Stores confirmed option in **MongoDB**.
- Updates question progression.

**Handled By**: **Yatin**

---

### 4. `GET /test/{test_id}/status`
**Purpose**: Retrieve test progress for showing a progress bar.

**Output**:
```json
{
  "answered_questions": number,
  "total_questions": number,
  "progress_percent": number
}
```

**Backend Logic**:
- Counts confirmed options stored in **MongoDB**.

**Handled By**: **Yatin**

---

### 5. `POST /score/{test_id}`
**Purpose**: Psychologist triggers scoring logic once test is completed.

**Input**:
```json
{
  "test_id": string
}
```

**Output**:
```json
{
  "emotional_distress": number,
  "conduct_problems": number,
  "hyperactivity": number,
  "peer_relationships": number,
  "prosocial_behavior": number,
  "overall_difficulty_score": number
}
```

**Backend Logic**:
- Reads all confirmed options from **MongoDB**.
- Applies SDQ scoring logic.

**Handled By**: **Yatin**

---

### 6. `GET /test/{test_id}/result`
**Purpose**: Fetch scoring results of a given test.

**Output**:
```json
{
  "score_result": {...},
  "evaluated_by": string,
  "timestamp": string
}
```

**Backend Logic**:
- Retrieves scores from **MongoDB**.

**Handled By**: **Yatin**

---

### 7. `GET /test/{test_id}/conversation`
**Purpose**: Psychologist reviews full conversation history.

**Output**:
```json
{
  "conversation": [
    {
      "role": "user" | "assistant",
      "message": string,
      "question_id": string,
      "timestamp": string
    }
  ]
}
```

**Backend Logic**:
- Retrieves vector-stored messages for that test.

**Handled By**: **Ansh**

---

### 8. `POST /child/new`
**Purpose**: Add a new child for testing.

**Input**:
```json
{
  "name": string,
  "age": number
}
```

**Output**:
```json
{
  "child_id": string,
  "test_id": string,
  "first_message": string
}
```

**Backend Logic**:
- Starts a new session and stores child info.

**Handled By**: **Adi + Yatin**

---

### 9. `GET /user/tests`
**Purpose**: Lists previous tests for the current user or psychologist.

**Output**:
```json
{
  "tests": [
    {
      "test_id": string,
      "child_name": string,
      "date": string,
      "status": "completed" | "pending",
      "scored": boolean
    }
  ]
}
```

**Handled By**: **Yatin**

---

### 10. `GET /chat/history?test_id=...`
**Purpose**: Psychologist views raw chat thread.

**Output**:
```json
{
  "history": [
    {
      "role": "user" | "assistant",
      "message": string,
      "timestamp": string
    }
  ]
}
```

**Backend Logic**:
- Accesses VectorDB to retrieve ordered chat flow.

**Handled By**: **Ansh**

