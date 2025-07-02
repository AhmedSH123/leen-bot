import json
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

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
        self.embeddings = [get_embedding(text) for text in self.text_chunks]
        self.index = NearestNeighbors(n_neighbors=5, metric="cosine")
        self.index.fit(self.embeddings)

    def rebuild_index(self, *files):
        self.load_data(files)
        self.embed_data()
        print(f"✅ Rebuilt index with {len(self.text_chunks)} text chunks.")

    def get_top_matches(self, question, k=5):
        q_embedding = get_embedding(question)
        D, I = self.index.kneighbors([q_embedding], n_neighbors=k)
        return [self.text_chunks[i] for i in I[0]]

    def answer_question(self, question: str) -> str:
        top_context = self.get_top_matches(question, k=5)
        context_text = "\n\n".join(top_context)

        return f"سؤالك: {question}\n\nالمعلومات ذات الصلة:\n{context_text}"