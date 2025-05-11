import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
REQUESTS_DIR = os.path.join(BASE_DIR, "demandes")
ARCHIVES_DIR = os.path.join(BASE_DIR, "archives")

os.makedirs(REQUESTS_DIR, exist_ok=True)
os.makedirs(ARCHIVES_DIR, exist_ok=True)

def create_request_file(type_document, infos_requises):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{type_document.replace(' ', '_')}_{timestamp}.json"
    filepath = os.path.join(REQUESTS_DIR, filename)

    data = {
        "type_document": type_document,
        "infos_requises": infos_requises,
        "infos_fournies": {key: "" for key in infos_requises},
        "etat": "en_cours",
        "created_at": timestamp
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath

def load_request(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_request(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_request(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def list_current_requests():
    return [os.path.join(REQUESTS_DIR, f)
            for f in os.listdir(REQUESTS_DIR)
            if f.endswith(".json")]

def list_archived_requests():
    return [os.path.join(ARCHIVES_DIR, f)
            for f in os.listdir(ARCHIVES_DIR)
            if f.endswith(".json")]

def archive_request(filepath):
    if os.path.exists(filepath):
        filename = os.path.basename(filepath)
        os.rename(filepath, os.path.join(ARCHIVES_DIR, filename))
