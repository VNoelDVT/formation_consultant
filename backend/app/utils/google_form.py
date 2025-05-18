import os
import pickle
import time
from backend.app.utils.mailer import send_mail
from backend.app.db.session_tracker import SessionTracker
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_PATH = "backend/app/utils/credentials.json"
TOKEN_PATH = "backend/app/utils/token.pkl"


def get_forms_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("forms", "v1", credentials=creds)


def fetch_latest_responses(form_id: str):
    service = get_forms_service()
    responses = service.forms().responses().list(formId=form_id).execute()
    return responses.get("responses", [])


def process_and_email_score(form_id: str, user_email: str, user_id: str):
    responses = fetch_latest_responses(form_id)
    if not responses:
        print("⚠️ Aucune réponse trouvée.")
        return

    tracker = SessionTracker(user_id)
    questions_data = tracker.get_latest_results().get("questions", [])
    incorrect = []

    latest_response = responses[-1]  # Dernière soumission
    answers = latest_response.get("answers", {})

    for i, q in enumerate(questions_data):
        correct = q.get("correct_answer")
        answer_data = answers.get(f"question{i}", {}).get("textAnswers", {}).get("answers", [{}])
        answer = answer_data[0].get("value", "") if answer_data else ""
        if answer != correct:
            incorrect.append((q["question"], answer))

    score = len(questions_data) - len(incorrect)
    total = len(questions_data)

    summary = f"✅ Résultat du quiz PRINCE2 : {score}/{total}\n\n"
    if incorrect:
        summary += "❌ Questions mal répondues :\n"
        for q_text, wrong in incorrect:
            summary += f"- {q_text}\n  → Votre réponse : {wrong}\n"

    send_mail(
        recipient=user_email,
        subject="Vos résultats PRINCE2",
        body=summary
    )


def create_google_form(questions: list, user_email: str = None, user_id: str = None) -> str:
    """
    Crée un Google Form dynamique depuis une liste de questions.
    Et si user_email et user_id sont fournis, prépare l'envoi automatique du résultat.
    """
    service = get_forms_service()

    NEW_FORM = {
        "info": {
            "title": "Quiz PRINCE2",
            "documentTitle": "Quiz PRINCE2 Auto-généré"
        }
    }

    form = service.forms().create(body=NEW_FORM).execute()
    form_id = form["formId"]

    requests = []
    for i, q in enumerate(questions):
        requests.append({
            "createItem": {
                "item": {
                    "title": q["question"],
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [{"value": ans} for ans in q["answers"]],
                                "shuffle": False
                            }
                        }
                    }
                },
                "location": {
                    "index": i
                }
            }
        })

    service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

    drive_service = build("drive", "v3", credentials=service._http.credentials)
    drive_service.permissions().create(
        fileId=form_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    # Facultatif : lancer l'envoi des résultats si on a les infos de l'utilisateur
    if user_email and user_id:
        from threading import Thread
        Thread(target=process_and_email_score, args=(form_id, user_email, user_id)).start()

    return f"https://docs.google.com/forms/d/{form_id}/viewform"

def get_form_responses(form_id: str):
    service = get_forms_service()
    response = service.forms().responses().list(formId=form_id).execute()
    return response.get("responses", [])
