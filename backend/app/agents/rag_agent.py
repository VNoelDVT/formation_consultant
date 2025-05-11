# === 🔧 Dépendances ===
import os
import json
import subprocess
import spacy
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    SpacyTextSplitter
)

from backend.app.utils.llm import generate_content
from backend.app.utils.auth import get_google_service
from backend.app.utils.google_drive import upload_to_gdrive
from backend.utils_request_manager import (
    create_request_file,
    load_request,
    save_request,
    delete_request,
    archive_request,
    list_current_requests
)

# === Mémoire persistante partagée ===
MEMORY_FILE = "global_memory.json"

GLOBAL_MEMORY = {
    "prenom": "",
    "nom": "",
    "adresse": "",
    "situation_familiale": "",
    "revenus": "",
    "métier": "",
    "ressources_financieres": "",
    "num_secu": "",
    "date_naissance": "",
    "lieu_naissance": "",
    "telephone": "",
    "email": "",
    "composition_foyer": "",
    "derniere_adresse": "",
    "motif_demande": "",
    "employeur": ""
}

AGENT_SWITCH = "admin"

def load_global_memory():
    global GLOBAL_MEMORY
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                GLOBAL_MEMORY.update(json.load(f))
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de la mémoire : {e}")

def save_global_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(GLOBAL_MEMORY, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde de la mémoire : {e}")

def admin_doc_agent(state: dict) -> dict:
    print("📄 Agent Documents Administratifs lancé")
    global AGENT_SWITCH
    AGENT_SWITCH = "admin"

    load_global_memory()

    user_message = state.get("user_message") or state.get("message", "")

    extraction_prompt = f"""Tu es un assistant administratif. Voici un message utilisateur : '{user_message}'.

        Si tu détectes des informations personnelles utiles pour remplir un document administratif (nom, adresse, revenus, etc.), retourne un **JSON PUR** (aucun mot autour !) du format suivant (même partiel) :

        {{
        "prenom": "",
        "nom": "",
        "adresse": "",
        "situation_familiale": "",
        "revenus": "",
        "métier": "",
        "ressources_financieres": "",
        "num_secu": "",
        "date_naissance": "",
        "lieu_naissance": "",
        "telephone": "",
        "email": "",
        "composition_foyer": "",
        "derniere_adresse": "",
        "motif_demande": "",
        "employeur": ""
        }}

        Sinon, réponds strictement par : null
    """

    extraction_result = generate_content(extraction_prompt).strip()
    print(f"🧠 Extraction des infos personnelles : {extraction_result}")

    if extraction_result.lower() != "null":
        try:
            extracted_data = json.loads(extraction_result)
            for k, v in extracted_data.items():
                if v:
                    GLOBAL_MEMORY[k] = v
            save_global_memory()
        except Exception as e:
            print(f"⚠️ Erreur de parsing mémoire : {e}")
        state["memory"] = GLOBAL_MEMORY.copy()

    current_doc_type = state.get("in_progress_doc_type")
    required_fields = state.get("required_fields", [])

    if not current_doc_type or not required_fields:
        classification_prompt = (
            f"Voici la demande utilisateur : '{user_message}'.\n\n"
            "Voici les documents disponibles et les champs requis :\n"
            "{\n"
            "  \"Demande de RSA / APL / autres aides\": [\"situation_familiale\", \"revenus\", \"composition_foyer\", \"derniere_adresse\"],\n"
            "  \"Demande de renouvellement de carte d’identité / passeport\": [\"nom\", \"prenom\", \"date_naissance\", \"lieu_naissance\", \"adresse\"]\n"
            "}\n\n"
            "Si tu reconnais une de ces demandes, retourne un **JSON PUR** comme ceci :\n"
            "{\n"
            "  \"est_document_admin\": true,\n"
            "  \"type_document\": \"Nom exact du document\",\n"
            "  \"infos_requises\": [\"liste des champs nécessaires\"]\n"
            "}\n\n"
            "Sinon, retourne : { \"est_document_admin\": false }"
        )

        classification_result = generate_content(classification_prompt)
        print("🧐 Résultat classification :", classification_result)

        try:
            parsed = json.loads(classification_result)
        except Exception as e:
            print(f"❌ Erreur parsing JSON : {e}")
            state["agent_response"] = "Je n’ai pas compris votre demande. Voici des exemples de documents administratifs reconnus."
            AGENT_SWITCH = "admin"
            state["switch"] = "admin"
            return state

        if not parsed.get("est_document_admin"):
            if state.get("in_progress_doc_type"):
                print("ℹ️ Pas de nouveau document détecté, mais un document est déjà en cours. On continue.")
                current_doc_type = state["in_progress_doc_type"]
                required_fields = state["required_fields"]
            else:
                state["agent_response"] = "Je gère uniquement les documents administratifs suivants. Merci de reformuler."
                AGENT_SWITCH = "default"
                state["switch"] = "default"
                return state
        else:
            current_doc_type = parsed["type_document"]
            required_fields = parsed["infos_requises"]
            state["in_progress_doc_type"] = current_doc_type
            state["required_fields"] = required_fields

    for field in required_fields:
        if field not in GLOBAL_MEMORY:
            GLOBAL_MEMORY[field] = ""

    missing_infos = [k for k in required_fields if not GLOBAL_MEMORY.get(k)]
    state["last_missing_infos"] = missing_infos

    if missing_infos:
        state["agent_response"] = (
            f"✅ Vous avez demandé le document : **{current_doc_type}**.\n\n"
            f"Pour le créer, il manque : {', '.join(missing_infos)}. Merci de compléter."
        )
        state["action_taken"] = "requesting_missing_info"
        AGENT_SWITCH = "admin"
        state["switch"] = "admin"
        return state

    AGENT_SWITCH = "default"
    state["switch"] = "default"
    memory_text = "\n".join([f"{k.capitalize()} : {v}" for k, v in GLOBAL_MEMORY.items() if v])

    doc_prompt = (
        f"Tu es un expert administratif. Rédige un document officiel : {current_doc_type}.\n"
        f"Voici les informations à utiliser :\n{memory_text}\n\n"
        "Le document doit être complet, formel et conforme aux normes administratives."
    )
    generated_doc = generate_content(doc_prompt)

    try:
        service = get_google_service('docs', 'v1')
        doc = service.documents().create(body={'title': current_doc_type}).execute()
        document_id = doc['documentId']
        service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': [{'insertText': {'location': {'index': 1}, 'text': generated_doc}}]}
        ).execute()

        state["google_doc_id"] = document_id
        state["google_doc_url"] = f"https://docs.google.com/document/d/{document_id}/edit"
        state["generated_doc_title"] = current_doc_type
        state["agent_response"] = f"✅ Le document **{current_doc_type}** a été généré avec succès : {state['google_doc_url']}"
        state["action_taken"] = "admin_doc_created_in_google_docs"
        state.pop("in_progress_doc_type", None)
        state.pop("required_fields", None)

    except Exception as e:
        state["agent_response"] = f"❌ Erreur lors de la création du Google Docs : {str(e)}"
        state["action_taken"] = "admin_doc_creation_failed"

    return state
