
import json
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = "mistral-saba-24b"

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text):
    return model.encode(text).tolist()

class LeenQABot:
    def __init__(self):
        self.text_chunks = []
        self.embeddings = []
        self.index = None

    def load_data(self, files: List[str]):
        self.text_chunks = []
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    for key in item:
                        if isinstance(item[key], str):
                            self.text_chunks.append(item[key])

    def embed_data(self):
        self.embeddings = np.array([get_embedding(text) for text in self.text_chunks])
        self.index = NearestNeighbors(n_neighbors=5, metric="cosine")
        self.index.fit(self.embeddings)

    def rebuild_index(self, *files):
        self.load_data(list(files))
        self.embed_data()
        print(f"✅ Rebuilt index with {len(self.text_chunks)} text chunks.")

    def get_top_matches(self, question, k=5):
        if self.index is None or len(self.embeddings) == 0:
            return []

        q_embedding = np.array([get_embedding(question)])  # wrap in NumPy array
        D, I = self.index.kneighbors(q_embedding, n_neighbors=k)
        return [self.text_chunks[i] for i in I[0]]

    def call_groq(self, prompt: str) -> str:
        if not GROQ_API_KEY:
            return "⚠️ GROQ_API_KEY not set."

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for Leen Training Platform."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error from Groq API: {response.status_code} - {response.text}"

    def answer_question(self, question: str) -> str:
        if self.index is None or len(self.embeddings) == 0:
            print("⚠️ No index available. Falling back to Groq.")
            return self._fallback_to_groq(question)

        top_context = self.get_top_matches(question, k=5)
        context_text = "\n\n".join(top_context)

        # If context is too weak, fallback
        if not context_text.strip() or len(context_text.strip()) < 100:
            print("🔁 Fallback to Groq triggered (context too weak)")
            return self._fallback_to_groq(question)

        print("✅ Answered from local index")
        return f"سؤالك: {question}\n\nالمعلومات ذات الصلة:\n{context_text}"

    def _is_generic_question(self, question, top_context):
        return all(len(text.strip()) < 10 for text in top_context)

    def _fallback_to_groq(self, question: str) -> str:
        print("⚙️  Using Groq to answer...")
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        chat_response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for the Leen training center."},
                {"role": "user", "content": question}
            ],
            temperature=0.7
        )

        return chat_response.choices[0].message.content or "❌ Groq returned no response."







