from app.agents.docs_tool import create_google_doc

if __name__ == '__main__':
    title = 'Demo Auto Doc'
    content = (
        "Ceci est un rapport automatique.\n"
        "Les prix sont bien alignés avec le marché.\n"
        "Rapport généré automatiquement 🚀."
    )

    document_id = create_google_doc(title, content)
    print(f"✅ Le document est ici : https://docs.google.com/document/d/{document_id}/edit")
