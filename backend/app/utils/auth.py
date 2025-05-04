import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.send'
]

def authenticate():
    print("👉 Running authentication...")

    if not os.path.exists('credentials.json'):
        print("❌ credentials.json NOT FOUND!")
    else:
        print("✅ Found credentials.json")

    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    with open('token.pkl', 'wb') as token:
        pickle.dump(creds, token)
    print("✅ Token saved as token.pkl")

def get_google_service(api_name, api_version):
    with open('token.pkl', 'rb') as token:
        creds = pickle.load(token)
    service = build(api_name, api_version, credentials=creds)
    return service
