# utils/rag_db.py
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class RAGDatabase:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.embeddings = []

    def load_documents(self, folder_path):
        for filename in os.listdir(folder_path):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                text = f.read()
                self.documents.append(text)

    def build_index(self):
        self.embeddings = self.model.encode(self.documents, convert_to_numpy=True)
        dim = self.embeddings[0].shape[0]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.embeddings)

    def retrieve(self, query, top_k=5):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, top_k)
        return [self.documents[i] for i in indices[0]]

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump((self.index, self.documents, self.embeddings), f)

    def load(self, path):
        with open(path, 'rb') as f:
            self.index, self.documents, self.embeddings = pickle.load(f)
