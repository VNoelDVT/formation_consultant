from app.agents.docs_tool import create_google_doc

def docs_agent_node(state: dict) -> dict:
    user_message = state.get("user_message", "")

    # Génération simple pour la démo (plus tard on pourra mettre du LLM)
    title = "Document créé par Agent"
    content = f"Contenu généré automatiquement pour : {user_message}"

    # Appel de l'outil Google Docs
    doc_info = create_google_doc(title, content)

    return {
        "action_taken": "Document créé dans Google Docs",
        "agent_response": (
            f"✅ Document créé avec succès !\n"
            f"ID: {doc_info['doc_id']}\n"
            f"URL: {doc_info['doc_url']}"
        )
    }
