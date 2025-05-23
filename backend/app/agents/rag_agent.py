# agents/prince2_agent.py
import json
import re
import os
from backend.app.utils.llm import generate_content
from backend.app.utils.mailer import send_mail
from backend.app.db.session_tracker import SessionTracker
from backend.app.rag_db import RAGDatabase
from backend.app.utils.google_docs import create_summary_doc

rag_db = RAGDatabase()

SESSION_PATH = "sessions"

def save_to_json(filename, data):
    if not os.path.exists(SESSION_PATH):
        os.makedirs(SESSION_PATH)
    with open(os.path.join(SESSION_PATH, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def prince2_agent(state: dict) -> dict:
    print("🔍 RAG agent for PRINCE2 training launched.")

    user_id = state.get("user_id", "default")
    tracker = SessionTracker(user_id=user_id)
    user_message = state.get("user_message") or state.get("message")
    print("Prompt user :", repr(user_message))

    # Si réponses présentes, ne pas forcer un user_message
    if not user_message and "answers" not in state:
        state["agent_response"] = "Je n’ai pas reçu de message. Peux-tu reformuler ?"
        state["switch"] = "default"
        return state

    # --- Détection d’intention de quiz ---
    question_request_prompt = f"""
        Tu es un assistant PRINCE2. Voici un message utilisateur : '{user_message}'.

        Si tu détectes une demande de quiz/formation PRINCE2, réponds UNIQUEMENT avec ce JSON :

        {{
        "is_quiz_request": true,
        "num_questions": 1
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
            json_text = match.group().replace("\\_", "_")
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
                questions = json.loads(match.group())
            else:
                raise ValueError("Aucun JSON valide détecté dans la réponse.")
        except Exception as e:
            print("❌ Erreur de parsing JSON des questions :", e)
            state["agent_response"] = "Je n’ai pas pu générer les questions du quiz. Merci de reformuler ou réessayer."
            state["switch"] = "default"
            state["action_taken"] = "quiz_generation_failed"
            return state

        session_id = tracker.get_new_session_id()
        save_to_json(f"{user_id}_questions_{session_id}.json", questions)

        state["questions"] = questions
        state["session_id"] = session_id

        state["agent_response"] = "Voici votre quiz PRINCE2. Veuillez répondre aux questions ci-dessous."
        state["action_taken"] = "quiz_inline"
        return state


    if "résumé" in user_message.lower() and "answers" in state:
        answers = state["answers"]
        session_id = state.get("session_id", tracker.get_last_session_id())
        resume_dir = "backend/app/data/resumes"
        os.makedirs(resume_dir, exist_ok=True)

        save_to_json(f"{user_id}_answers_{session_id}.json", answers)

        # Chargement questions
        with open(os.path.join(SESSION_PATH, f"{user_id}_questions_{session_id}.json"), encoding="utf-8") as fq:
            questions = json.load(fq)

        # 🧠 Prompt LLM pour résumé basé sur les JSON
        structured_prompt = f"""
    Tu es un assistant pédagogique expert PRINCE2.

    Voici les questions posées à l'utilisateur (au format JSON) :
    {json.dumps(questions, indent=2, ensure_ascii=False)}

    Et voici les réponses qu'il a données :
    {json.dumps(answers, indent=2, ensure_ascii=False)}

    Lis les questions et les bonnes réponses intégrées, puis compare-les avec les réponses de l'utilisateur.
    Génère un résumé clair, structuré et bienveillant avec les sections suivantes :

    1. Introduction
    2. Score global (ex: "7 bonnes réponses sur 10")
    3. Ce que l'utilisateur maîtrise (questions réussies)
    4. Ce qu'il doit retravailler (questions mal répondues, avec explication de la bonne réponse)
    5. Conseils personnalisés pour progresser

    N'invente rien. Base-toi uniquement sur les JSON.
    """

        summary_text = generate_content(structured_prompt)

        # Sauvegarde locale du résumé
        resume_filename = f"{user_id}_resume_{session_id}.txt"
        resume_path = os.path.join(resume_dir, resume_filename)
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        # Google Doc (optionnel si utile en PDF/Docs)
        doc_url = create_summary_doc(summary_text, title="Résumé session PRINCE2")

        # Envoi mail
        user_email = state.get("user_email", "valentin.noel@devoteam.com")
        send_mail(
            to_email=user_email,
            subject="📘 Votre résumé de session PRINCE2 est prêt",
            body=f"Bonjour,\n\nVoici votre résumé de session PRINCE2 : {doc_url}\n."
        )

        state["agent_response"] = f"Résumé généré : {doc_url} (et stocké sous {resume_filename})"
        state["summary_url"] = doc_url
        state["summary_file"] = resume_filename
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