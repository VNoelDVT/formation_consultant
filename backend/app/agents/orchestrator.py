from langgraph.graph import StateGraph, END, START
from backend.app.agents.rag_agent import prince2_agent

def create_prince2_graph():
    workflow = StateGraph(dict)
    workflow.add_node("prince2", prince2_agent)
    workflow.add_edge(START, "prince2")
    workflow.add_edge("prince2", END)
    return workflow.compile()

agent_graph = create_prince2_graph()
