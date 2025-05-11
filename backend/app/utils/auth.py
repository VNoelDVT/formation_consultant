import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.send'
]

# Détermine le chemin absolu vers le dossier backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, 'token.pkl')
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')

def authenticate():
    print("👉 Running authentication...")

    if not os.path.exists(CREDENTIALS_PATH):
        print("❌ credentials.json NOT FOUND at:", CREDENTIALS_PATH)
        return

    print("✅ Found credentials.json")
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=8080)

    with open(TOKEN_PATH, 'wb') as token:
        pickle.dump(creds, token)
    print(f"✅ Token saved at: {TOKEN_PATH}")

def get_google_service(api_name, api_version):
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token file not found at: {TOKEN_PATH}")
    
    with open(TOKEN_PATH, 'rb') as token:
        creds = pickle.load(token)
    
    service = build(api_name, api_version, credentials=creds)
    return service
