from rag_db import RAGDatabase
from utils.pdf_converter import convert_pdfs_to_txt

if __name__ == "__main__":
    print("🔄 Conversion des PDFs PRINCE2 en .txt...")
    convert_pdfs_to_txt("data/pdf_source", "data/prince2")


    print("📚 Indexation des documents avec ChromaDB...")
    db = RAGDatabase()
    db.clear_collection()  # ⚠️ vide l’index avant de recharger
    db.load_documents("data/prince2")
    db.index_documents()
    print("✅ Indexation terminée.")
