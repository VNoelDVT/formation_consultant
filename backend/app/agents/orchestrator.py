from langgraph.graph import StateGraph, END
from backend.app.agents.rag_agent import (
    rag_index_agent,
    rag_search_agent,
    rag_generate_doc_agent,
    gantt_agent
)

# Créer le graphe LangGraph avec l'agent Gantt ajouté
def create_rag_graph():
    workflow = StateGraph(dict)

    # Étapes / agents
    workflow.add_node("index", rag_index_agent)
    workflow.add_node("search", rag_search_agent)
    workflow.add_node("gantt", gantt_agent)
    workflow.add_node("generate", rag_generate_doc_agent)

    # Transitions
    workflow.set_entry_point("index")
    workflow.add_edge("index", "search")
    workflow.add_edge("search", "gantt")
    workflow.add_edge("gantt", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


# On compile et expose le graphe sous le nom utilisé dans main.py
agent_graph = create_rag_graph()
