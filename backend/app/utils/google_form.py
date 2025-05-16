import os
import pickle
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

def create_google_form(questions: list) -> str:
    """
    Crée un Google Form dynamique depuis une liste de questions de type :
    {
        "question": "Quelle est la bonne réponse ?",
        "answers": ["Réponse A", "Réponse B", "Réponse C", "Réponse D"],
        "correct_answer": "Réponse B"
    }
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
    for q in questions:
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
                    "index": 0
                }
            }
        })

    service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

    # Permettre la lecture via URL publique
    drive_service = build("drive", "v3", credentials=service._http.credentials)
    drive_service.permissions().create(
        fileId=form_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    return f"https://docs.google.com/forms/d/{form_id}/viewform"
