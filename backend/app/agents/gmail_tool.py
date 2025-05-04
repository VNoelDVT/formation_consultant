from app.utils.auth import get_google_service
import base64
from email.mime.text import MIMEText

def send_email(recipient, subject, message_text):
    """
    Envoie un email via Gmail API.
    """
    service = get_google_service('gmail', 'v1')
    
    # 1️⃣ Construire le message MIME
    message = MIMEText(message_text)
    message['to'] = recipient
    message['subject'] = subject

    # 2️⃣ Encoder le message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # 3️⃣ Envoyer le mail
    send_message = service.users().messages().send(
        userId="me",
        body={'raw': raw_message}
    ).execute()
    
    print(f"✅ Email envoyé à {recipient} (ID: {send_message['id']})")
    return send_message
