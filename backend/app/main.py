from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents.docs_tool import create_google_doc
from app.agents.rag_agent import index_document 
from app.agents.rag_agent import search_relevant_chunks
from app.utils.llm import generate_doc_content
from app.utils.auth import get_google_service


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, it works!"}


class DocRequest(BaseModel):
    title: str
    content: str

@app.post("/create-doc")
def create_doc(doc_request: DocRequest):
    try:
        result = create_google_doc(doc_request.title, doc_request.content)
        return {
            "status": "success",
            "doc_id": result['doc_id'],
            "doc_url": result['doc_url']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class IndexRequest(BaseModel):
    project_id: str
    document_text: str
    strategy: str = "recursive"

@app.post("/index-project")
def index_project(req: IndexRequest):
    try:
        index_document(
            document_text=req.document_text,
            project_id=req.project_id,
            strategy=req.strategy
        )
        return {"status": "success", "message": "Projet indexé ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class SmartDocRequest(BaseModel):
    user_input: str
    doc_title: str
    n_results: int = 3

@app.post("/create-doc-smart")
def create_doc_smart(req: SmartDocRequest):
    try:
        # 🔎 Étape 1 : Recherche vectorielle
        relevant_chunks = search_relevant_chunks(req.user_input, req.n_results)
        context = "\n\n".join(relevant_chunks)

        # 🧠 Étape 2 : Création du prompt augmenté
        final_prompt = (
            f"Contexte :\n{context}\n\n"
            f"Tâche : {req.user_input}"
        )

        # 🤖 Étape 3 : Appel NVIDIA API
        generated_content = generate_doc_content(final_prompt)

        # 📝 Étape 4 : Création Google Docs
        service = get_google_service('docs', 'v1')
        doc = service.documents().create(body={'title': req.doc_title}).execute()
        document_id = doc['documentId']

        requests = [
            {'insertText': {
                'location': {'index': 1},
                'text': generated_content
            }}
        ]
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        return {
            "status": "success",
            "doc_id": document_id,
            "doc_url": f"https://docs.google.com/document/d/{document_id}/edit"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

