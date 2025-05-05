from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.app.agents.docs_tool import create_google_doc
from backend.app.agents.rag_agent import index_document, search_relevant_chunks
from backend.app.utils.llm import generate_doc_content
from backend.app.utils.auth import get_google_service
from backend.app.agents.orchestrator import agent_graph

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
        # Étape 1 : Recherche vectorielle
        relevant_chunks = search_relevant_chunks(req.user_input, req.n_results)
        context = "\n\n".join(relevant_chunks)

        # Étape 2 : Création du prompt augmenté
        final_prompt = (
            f"Contexte :\n{context}\n\n"
            f"Tâche : {req.user_input}"
        )

        # Étape 3 : Appel NVIDIA API
        generated_content = generate_doc_content(final_prompt)

        # Étape 4 : Création Google Docs
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


# 🔥 NOUVELLE classe qui couvre tout ce qu'il faut pour le graphe complet
class FullAgentRequest(BaseModel):
    message: str
    project_id: str
    document_text: str
    strategy: str = "recursive"
    n_results: int = 3


@app.post("/agent-run")
def run_agent(req: FullAgentRequest):
    try:
        # Initialiser l'état complet avec toutes les infos reçues
        state = req.dict()

        # Lancer le graphe LangGraph
        result = agent_graph.invoke(state)

        # Vérifier le type pour éviter les erreurs
        if isinstance(result, dict):
            return {
                "status": "success",
                "agent_response": result.get("agent_response", "Aucune réponse"),
                "action_taken": result.get("action_taken", "Aucune action"),
                "google_doc_url": result.get("google_doc_url"),
                "google_doc_id": result.get("google_doc_id"),
                "generated_doc": result.get("generated_doc", None),
                "generated_doc_title": result.get("generated_doc_title"),
                "indexing_done": result.get("indexing_done"),
                "rag_results": result.get("rag_results"),
                "gantt_image_url": result.get("gantt_image_url"),
                "google_slides_url": result.get("google_slides_url"),
                "history": result.get("history", [])
            }

        else:
            # Si c’est autre chose qu’un dict (erreur logique interne)
            return {
                "status": "error",
                "message": f"Résultat inattendu : {result}"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
