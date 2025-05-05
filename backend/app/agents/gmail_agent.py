from app.agents.gmail_tool import send_email  # On suppose que tu as ce tool prêt

def gmail_agent_node(state: dict) -> dict:
    """
    Analyse le message utilisateur et envoie un mail si nécessaire.
    """
    print("📧 Gmail Agent activé...")

    # Récupérer le message utilisateur depuis l'état
    user_message = state.get("user_message", "")

    # Démo : envoie toujours un mail (ajuste ta logique plus tard si besoin)
    subject = "Mail automatique depuis l'agent"
    body = f"Contenu généré automatiquement pour : {user_message}"
    recipient = "valentin.noel@devoteam.com"  

    try:
        send_email(recipient, subject, body)
        return {
            "agent_response": f"✅ Email envoyé à {recipient} avec succès !",
            "action_taken": "Envoi Email"
        }
    except Exception as e:
        return {
            "agent_response": f"⚠️ Erreur lors de l'envoi de l'email : {str(e)}",
            "action_taken": "Erreur Email"
        }
