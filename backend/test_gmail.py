from app.agents.gmail_tool import send_email

if __name__ == '__main__':
    recipient = 'valentin.noel@devoteam.com'  # ex : valentin.noel@monmail.com
    subject = 'Test auto - Rapport'
    message_text = (
        "Bonjour,\n\n"
        "Ceci est un test automatique envoyé via la Gmail API.\n"
        "Le lien du rapport : https://docs.google.com/document/d/ID_DU_DOC/edit\n\n"
        "Bonne journée ! 🚀"
    )

    send_email(recipient, subject, message_text)
