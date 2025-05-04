from app.utils.auth import get_google_service

def create_google_doc(title, content):
    """
    Crée un Google Docs avec un titre et un contenu initial.
    Retourne l'ID du document et son URL.
    """
    service = get_google_service('docs', 'v1')

    # 1️⃣ Créer le document
    doc = service.documents().create(body={'title': title}).execute()
    document_id = doc['documentId']
    print(f"✅ Nouveau Google Doc créé avec ID : {document_id}")

    # 2️⃣ Ecrire le contenu
    requests = [
        {'insertText': {
            'location': {'index': 1},
            'text': content
        }}
    ]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    print("✅ Contenu ajouté au Google Doc")

    # 3️⃣ Construire le lien Google Docs
    doc_url = f"https://docs.google.com/document/d/{document_id}/edit"

    return {
        "doc_id": document_id,
        "doc_url": doc_url
    }
