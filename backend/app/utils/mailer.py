import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Variables d’environnement (ou hardcodées pour test)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "tonemail@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "mot_de_passe_app")

def send_mail(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email envoyé à {to_email}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du mail : {e}")
