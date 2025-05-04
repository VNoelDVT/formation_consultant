from fastapi import APIRouter
from app.agents.sheets_tool import create_new_sheet, write_prices_to_sheet
from app.agents.docs_tool import create_google_doc
from app.agents.gmail_tool import send_email

router = APIRouter()

@router.post("/process")
async def full_process(recipient_email: str):
    # 1️⃣ Créer Google Sheets
    sheet_title = "Rapport Prix Auto"
    spreadsheet_id, first_sheet_name = create_new_sheet(sheet_title)
    data = [
        ['Marque', 'Prix'],
        ['Lenovo', '1000'],
        ['Dell', '1200'],
        ['HP', '900']
    ]
    write_prices_to_sheet(spreadsheet_id, first_sheet_name, data)

    # 2️⃣ Créer Google Docs
    doc_title = "Rapport Automatique"
    doc_content = (
        f"Bonjour,\n\nVoici le rapport automatique des prix.\n\n"
        f"Les données sont disponibles dans la Google Sheets : https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit\n\n"
        f"Merci ! 🚀"
    )
    document_id = create_google_doc(doc_title, doc_content)

    # 3️⃣ Envoyer Email
    subject = "Votre rapport automatique est prêt"
    message_text = (
        f"Bonjour,\n\n"
        f"Votre rapport est prêt !\n"
        f"- Google Sheets : https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit\n"
        f"- Google Docs : https://docs.google.com/document/d/{document_id}/edit\n\n"
        f"Bonne journée ! 🚀"
    )
    send_email(recipient_email, subject, message_text)

    return {
        "message": "✅ Processus complet terminé",
        "google_sheets_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
        "google_docs_url": f"https://docs.google.com/document/d/{document_id}/edit"
    }
