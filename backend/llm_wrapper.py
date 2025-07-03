from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import requests
import torch

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


class LMStudioChat:
    def __init__(self, model="[INSERT MODEL NAME]", api_url="[INSERT API URL]"):
        self.vector_store = [] # for all prompts and history
        self.api_url = api_url
        self.model = model
        self.headers = {"Content-Type": "application/json"}
        self.system_prompt = ""
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def ask(self, prompt):

        prompt_embedding = embedding_model.encode(prompt, convert_to_tensor=True)

        if self.vector_store:
            past_embeddings = [entry["embedding"] for entry in self.vector_store]
            past_embeddings_tensor = torch.stack(past_embeddings)
            #cosine similarity to see how close updated history is to what is already saved
            scores = util.pytorch_cos_sim(prompt_embedding, past_embeddings_tensor)[0] 
            k = min(3, len(scores))  # avoid asking for more scores than exist
            top_scores = scores.topk(k)
            top_texts = [self.vector_store[i]["text"] for i in top_scores[1]]
            context = "\n".join(top_texts)
        else:
            context = ""

        reduced_prompt = f"{context}\n[User]: {prompt}"
        self.history.append({"role": "user", "content": reduced_prompt})

        self.vector_store.append({
        "text": prompt,
        "role": "user",
        "embedding": prompt_embedding
        })

        payload = {
            "model": self.model,
            "messages": self.history
        }

        response = requests.post(self.api_url, headers=self.headers, json=payload)

        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": reply})
            self.vector_store.append({
            "text": reply,
            "role": "assistant",
            "embedding": embedding_model.encode(reply, convert_to_tensor=True)
        })
            return reply
        else:
            return f"Error: {response.status_code} - {response.text}"
        


