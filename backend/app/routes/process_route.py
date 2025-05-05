from fastapi import APIRouter, Request
from app.agents.orchestrator import create_graph

router = APIRouter()

@router.post("/process")
async def process_route(request: Request):
    body = await request.json()
    user_input = body.get("input")

    graph = create_graph()
    initial_state = {"input": user_input}

    # Exécute le graphe complet
    result = graph.invoke(initial_state)

    return {"result": result}
