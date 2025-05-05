from app.agents.sheets_tool import create_new_sheet

def sheets_agent(state: dict) -> dict:
    print("Running Sheets Agent")
    gmail_data = state.get("gmail_result")
    result = f"Updated sheets with: {gmail_data}"
    state["sheets_result"] = result
    return state
