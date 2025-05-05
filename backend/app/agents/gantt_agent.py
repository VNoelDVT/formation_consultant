import subprocess

def gantt_agent(state: dict) -> dict:
    print("📊 Agent Gantt lancé")

    user_message = state.get("user_message") or state.get("message", "")

    # 1️⃣ Vérifier si la demande parle de Gantt
    classification_prompt = (
        f"Voici la demande : '{user_message}'. "
        "Réponds simplement par OUI si la demande implique de créer un diagramme de Gantt, sinon NON."
    )
    decision = generate_doc_content(classification_prompt).strip().lower()

    print(f"💡 Décision du LLM : {decision}")

    if "oui" in decision:
        # 2️⃣ Générer le code Python pour le diagramme
        gantt_code_prompt = (
            f"À partir de cette demande : '{user_message}', "
            "génère du code Python utilisant plotly qui crée un diagramme de Gantt. "
            "Assure-toi que le code sauvegarde l'image dans un fichier 'gantt_diagram.png'. "
            "Complète les étapes manquantes si besoin."
        )
        generated_code = generate_doc_content(gantt_code_prompt)
        print("🛠️ Code généré par le LLM :\n", generated_code)

        # 3️⃣ Sauvegarder le code dans un fichier temporaire
        with open("temp_gantt.py", "w", encoding="utf-8") as f:
            f.write(generated_code)

        # 4️⃣ Exécuter le code
        try:
            subprocess.run(["python", "temp_gantt.py"], check=True)
            state["gantt_image"] = "gantt_diagram.png"
            state["agent_response"] = "Diagramme de Gantt généré avec succès ✅"
            state["action_taken"] = "gantt_created"
        except Exception as e:
            state["agent_response"] = f"Erreur lors de la génération du diagramme : {str(e)}"
            state["action_taken"] = "gantt_failed"

    else:
        state["agent_response"] = "Aucune génération de diagramme nécessaire."
        state["action_taken"] = "no_action"

    return state
