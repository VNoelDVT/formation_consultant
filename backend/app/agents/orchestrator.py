from langgraph.graph import StateGraph, END, START
from backend.app.agents.rag_agent import admin_doc_agent

# Graphe simplifié sans orchestrateur : uniquement admin_doc_agent

def create_admin_only_graph():
    workflow = StateGraph(dict)

    # Un seul agent
    workflow.add_node("admin", admin_doc_agent)

    # START => admin => END
    workflow.add_edge(START, "admin")
    workflow.add_edge("admin", END)

    return workflow.compile()


# Expose le graphe limité à admin uniquement
agent_graph = create_admin_only_graph()
