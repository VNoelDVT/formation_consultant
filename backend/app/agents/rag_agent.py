# agents/prince2_agent.py
import json
import re
from backend.app.utils.llm import generate_content
from backend.app.utils.google_form import create_google_form
from backend.app.utils.mailer import send_mail
from backend.app.db.session_tracker import SessionTracker
from backend.app.rag_db import RAGDatabase
from backend.app.utils.google_docs import create_summary_doc

rag_db = RAGDatabase()

def prince2_agent(state: dict) -> dict:
    print("🔍 RAG agent for PRINCE2 training launched.")

    tracker = SessionTracker(user_id=state.get("user_id", "default"))
    user_message = state.get("user_message") or state.get("message")
    print("Prompt user :", repr(user_message))

    if not user_message:
        state["agent_response"] = "Je n’ai pas reçu de message. Peux-tu reformuler ?"
        state["switch"] = "default"
        return state

    # --- Détection d’intention de quiz ---
    question_request_prompt = f"""
        Tu es un assistant PRINCE2. Voici un message utilisateur : '{user_message}'.

        Si tu détectes une demande de quiz PRINCE2, réponds UNIQUEMENT avec ce JSON :

        {{
        "is_quiz_request": true,
        "num_questions": 10
        }}

        Si le message précise un nombre de questions, remplace la valeur.

        Sinon, réponds strictement :

        {{ "is_quiz_request": false, "num_questions": 0 }}
        """

    llm_response = generate_content(question_request_prompt)
    print("🧠 Réponse brute du LLM :", repr(llm_response))

    try:
        match = re.search(r"\{.*?\}", llm_response, re.DOTALL)
        if match:
            json_text = match.group().replace("\\_", "_")  # ← corrige les échappements invalides
            decision = json.loads(json_text)
        else:
            raise ValueError("❌ Aucun JSON détecté dans la réponse LLM.")
    except Exception as e:
        print("❌ Erreur de parsing JSON :", e)
        state["agent_response"] = "Je n’ai pas compris votre demande. Pouvez-vous reformuler?"
        state["switch"] = "default"
        return state

    # --- Si quiz demandé ---
    if decision["is_quiz_request"]:
        print("🧠 Création du quiz...")
        previous_errors = tracker.get_errors_by_topic()
        print("🧠 Erreurs précédentes :", previous_errors)

        if previous_errors:
            user_message += " " + " ".join(previous_errors)

        retrieved_docs = rag_db.retrieve(user_message, top_k=5)
        context = "\n---\n".join(retrieved_docs)

        generation_prompt = f"""Based on this PRINCE2 training material:
        {context}

        Create {decision['num_questions']} multiple-choice questions with 4 options.
        Specify the correct one. Focus more on these weak areas: {', '.join(previous_errors) if previous_errors else 'general PRINCE2 knowledge'}.

        Return a JSON list like:
        [
        {{
            "question": "...",
            "answers": ["A", "B", "C", "D"],
            "correct_answer": "B"
        }},
        ...
        ]
        """
        print("🧠 Generation prompt :", generation_prompt)
        llm_output = generate_content(generation_prompt)
        print("🧠 Output du LLM (questions):", repr(llm_output))

        try:
            match = re.search(r"\[\s*{.*}\s*]", llm_output, re.DOTALL)
            if match:
                cleaned = match.group()
                questions = json.loads(cleaned)
            else:
                raise ValueError("Aucun JSON valide détecté dans la réponse.")
        except Exception as e:
            print("❌ Erreur de parsing JSON des questions :", e)
            state["agent_response"] = "Je n’ai pas pu générer les questions du quiz. Merci de reformuler ou réessayer."
            state["switch"] = "default"
            state["action_taken"] = "quiz_generation_failed"
            return state

        form_url = create_google_form(questions)
        tracker.store_questions(questions)

        # ✉️ Envoi par mail
        user_email = state.get("user_email", "valentin.noel@devoteam.com")
        send_mail(
            to_email=user_email,
            subject="📘 Votre questionnaire PRINCE2 est prêt",
            body=f"Bonjour,\n\nVoici votre formulaire PRINCE2 : {form_url}\nBonne chance !"
        )

        state["agent_response"] = f"Formulaire PRINCE2 généré : {form_url} (envoyé aussi par mail ✅)"
        state["form_url"] = form_url
        state["action_taken"] = "quiz_created"
        return state

    # --- Si demande de résumé ---
    if "résumé" in user_message.lower():
        results = tracker.get_latest_results()
        summary_prompt = f"""Voici les résultats du test PRINCE2 : {json.dumps(results, indent=2)}.

Rédige un résumé en français indiquant les points maîtrisés et les points à améliorer.
Sois bienveillant, structuré et professionnel. Le résumé doit être prêt à être envoyé à l'utilisateur.
"""
        summary_text = generate_content(summary_prompt)
        doc_url = create_summary_doc(summary_text, title="Résumé session PRINCE2")

        state["agent_response"] = f"Résumé généré : {doc_url}"
        state["summary_url"] = doc_url
        state["action_taken"] = "summary_created"
        return state

    # --- Réponse experte Devoteam par défaut ---
    state["agent_response"] = (
        "En tant qu’expert Devoteam en agilité et en PRINCE2, "
        "je peux vous proposer un quiz pour tester vos connaissances "
        "ou générer un résumé de votre progression. Dites-moi ce que vous préférez !"
    )
    state["switch"] = "default"
    return state
