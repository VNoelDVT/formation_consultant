from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter, SpacyTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import spacy

client = chromadb.PersistentClient(path="chromadb_storage")
collection = client.get_or_create_collection("projects")

embedder = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("fr_core_news_sm")

def get_chunks(text, strategy="recursive", chunk_size=500, chunk_overlap=50):
    if strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strategy == "markdown":
        splitter = MarkdownTextSplitter()
    elif strategy == "spacy":
        splitter = SpacyTextSplitter(pipeline=nlp)
    else:
        raise ValueError("Unsupported strategy")
    return splitter.split_text(text)

def index_document(document_text, project_id, strategy="recursive"):
    print(f"🚀 Indexation du projet {project_id} avec stratégie '{strategy}'")
    chunks = get_chunks(document_text, strategy=strategy)
    embeddings = [embedder.encode(chunk).tolist() for chunk in chunks]
    for idx, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{project_id}_{idx}"],
            documents=[chunk],
            embeddings=[embeddings[idx]]
        )
    print(f"✅ {len(chunks)} chunks indexés pour le projet {project_id}")

def search_relevant_chunks(query, n_results=3):
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['documents'][0]
