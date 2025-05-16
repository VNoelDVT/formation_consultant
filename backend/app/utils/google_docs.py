from backend.app.utils.auth import get_google_service

def create_summary_doc(text: str, title: str = "Résumé PRINCE2") -> str:
    service = get_google_service("docs", "v1")
    doc = service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    requests = [{
        "insertText": {
            "location": {"index": 1},
            "text": text
        }
    }]

    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()

    # Rendre le document public
    drive_service = get_google_service("drive", "v3")
    drive_service.permissions().create(
        fileId=doc_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"
