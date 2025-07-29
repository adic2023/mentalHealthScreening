
from sentence_transformers import SentenceTransformer
from db.mongo_handler import store_vector_response

model=SentenceTransformer("all-MiniLM-L6-v2")  # Load once

def embed_text(text: str):
    return model.encode(text).tolist()

def store_vector(test_id: str, question_index: int, vector: list, text: str):
    store_vector_response(test_id, question_index, vector, text)  #actual storage
    print(f"[Vector DB] Stored for test {test_id}, Q{question_index}: Text = {text[:30]}..., Embedding Length = {len(vector)}")


# store in mogodb??

'''

append in mongo_handler
def store_vector_response(test_id, question_index, vector, text):
    collection.update_one(
        {"test_id": test_id},
        {
            "$push": {
                "vector_responses": {
                    "question_index": question_index,
                    "text": text,
                    "embedding": vector
                }
            }
        }
    )

    
in chat, in respond add:
from db.vector_store import embed_text, store_vector

# Inside the try block
user_text = req.chat_history[-1]["content"] if req.chat_history else ""
vector = embed_text(user_text)
store_vector(test_id="unknown", question_index=question_index, vector=vector, text=user_text)

    

'''