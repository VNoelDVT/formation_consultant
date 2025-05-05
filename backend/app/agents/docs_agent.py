from backend.app.agents.docs_tool import create_google_doc

def docs_agent(state: dict) -> dict:
    print("Running Docs Agent")
    # Par ex : tu récupères l'input & fais un traitement fictif
    input_data = state.get("input")
    result = f"Processed docs for: {input_data}"
    state["docs_result"] = result
    return state
