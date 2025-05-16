import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

class RAGDatabase:
    def __init__(self, db_path="backend/app/db/chroma", collection_name="prince2", model_name="all-MiniLM-L6-v2"):
        self.client = PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.encoder = SentenceTransformer(model_name)

    def load_documents(self, folder_path):
        self.docs = []
        self.metadatas = []
        self.ids = []

        for idx, filename in enumerate(os.listdir(folder_path)):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    text = f.read()
                    self.docs.append(text)
                    self.metadatas.append({"filename": filename})
                    self.ids.append(f"doc_{idx}")

        print(f"📄 {len(self.docs)} documents chargés depuis {folder_path}")


    def index_documents(self):
        if not self.docs:
            print("⚠️ Aucun document à indexer. As-tu bien appelé load_documents() ?")
            return

        embeddings = self.encoder.encode(self.docs).tolist()
        self.collection.add(
            documents=self.docs,
            embeddings=embeddings,
            metadatas=self.metadatas,
            ids=self.ids
        )


    def retrieve(self, query: str, top_k=5):
        query_embedding = self.encoder.encode([query])[0].tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results['documents'][0] if results and results['documents'] else []

    def clear_collection(self):
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)

