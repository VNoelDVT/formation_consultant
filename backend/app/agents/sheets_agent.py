from app.agents.sheets_tool import create_new_sheet

def sheets_agent_node(state: dict) -> dict:
    """
    Analyse le message utilisateur et crée un Google Sheet si besoin.
    """
    print("📊 Sheets Agent activé...")

    user_message = state.get("user_message", "")

    # Vérifie si le message demande la création d'un Google Sheet
    if "sheet" in user_message.lower() or "tableur" in user_message.lower():
        title = "Sheet auto créé par l'agent"
        data = [
            ["Colonne 1", "Colonne 2"],
            ["Valeur A", "Valeur B"],
        ]
        sheet_url = create_new_sheet(title, data)
        return {
            "agent_response": f"✅ Google Sheet créé ici : {sheet_url}",
            "action_taken": "Création Google Sheet"
        }
    else:
        return {
            "agent_response": "ℹ️ Rien à faire pour Sheets.",
            "action_taken": "Aucune action Sheets"
        }
