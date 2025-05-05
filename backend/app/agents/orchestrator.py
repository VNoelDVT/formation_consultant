from langgraph.graph import StateGraph, END
from app.agents.docs_agent import docs_agent_node
from app.agents.sheets_agent import sheets_agent_node
from app.agents.gmail_agent import gmail_agent_node

# ✅ Créer le graphe LangGraph avec dict directement
workflow = StateGraph(dict)

# Ajout des nœuds (agents)
workflow.add_node("docs_agent", docs_agent_node)
workflow.add_node("sheets_agent", sheets_agent_node)
workflow.add_node("gmail_agent", gmail_agent_node)

# Exemple de routing (simple règle de mot-clé)
def route_request(state: dict):
    message = state.get("user_message", "").lower()
    if "document" in message or "doc" in message:
        return "docs_agent"
    elif "sheet" in message or "spreadsheet" in message or "tableur" in message:
        return "sheets_agent"
    elif "email" in message or "mail" in message:
        return "gmail_agent"
    else:
        return None  # aucun agent trouvé

# ✅ Ajout du routeur en tant que nœud
workflow.add_node("router", route_request)

# ✅ Set entry point par son nom
workflow.set_entry_point("router")

# Chaque agent revient à la fin
workflow.add_edge("docs_agent", END)
workflow.add_edge("sheets_agent", END)
workflow.add_edge("gmail_agent", END)

# Compiler le graphe
agent_graph = workflow.compile()
