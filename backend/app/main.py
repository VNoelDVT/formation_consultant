from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.app.utils.llm import generate_content
from backend.app.utils.auth import get_google_service
from backend.app.agents.orchestrator import agent_graph
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour tout autoriser (dev). Tu peux restreindre à ["http://localhost:5173"] après.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, it works!"}

# NOUVELLE classe qui couvre tout ce qu'il faut pour le graphe complet
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
