from app.agents.gmail_tool import send_email  # On suppose que tu as ce tool prêt

def gmail_agent(state: dict) -> dict:
    print("Running Gmail Agent")
    docs_data = state.get("docs_result")
    result = f"Sent email based on: {docs_data}"
    state["gmail_result"] = result
    return state