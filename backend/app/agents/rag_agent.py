from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter, SpacyTextSplitter
from sentence_transformers import SentenceTransformer
from backend.app.utils.llm import generate_doc_content
from backend.app.utils.auth import get_google_service 
from backend.app.utils.google_drive import upload_to_gdrive
import subprocess
import chromadb
import spacy
import os

# === Fonctions utilitaires ===
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
chromadb_path = os.path.join(backend_dir, "chromadb_storage")

client = chromadb.PersistentClient(path=chromadb_path)

collection = client.get_or_create_collection("projects")

embedder = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("fr_core_news_sm")

def get_chunks(text, strategy="recursive", chunk_size=500, chunk_overlap=50):
    if strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strategy == "markdown":
        splitter = MarkdownTextSplitter()
    elif strategy == "spacy":
        splitter = SpacyTextSplitter(pipeline=nlp)
    else:
        raise ValueError("Unsupported strategy")
    return splitter.split_text(text)

def index_document(document_text, project_id, strategy="recursive"):
    print(f"🚀 Indexation du projet {project_id} avec stratégie '{strategy}'")
    chunks = get_chunks(document_text, strategy=strategy)
    embeddings = [embedder.encode(chunk).tolist() for chunk in chunks]
    for idx, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{project_id}_{idx}"],
            documents=[chunk],
            embeddings=[embeddings[idx]]
        )
    print(f"✅ {len(chunks)} chunks indexés pour le projet {project_id}")

def search_relevant_chunks(query, n_results=3):
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['documents'][0]

# === 🚀 Nouveaux agents LangGraph ===

def rag_index_agent(state: dict) -> dict:
    if not state.get("document_text"):
        print("⚠️ Aucun document fourni : on saute l'indexation.")
        state["indexing_done"] = "Pas de document à indexer."
        return state

    print("📥 Agent RAG Index lancé")

    project_id = state.get("project_id", "default_project")
    document_text = state.get("document_text", "")
    strategy = state.get("strategy", "recursive")

    index_document(
        document_text=document_text,
        project_id=project_id,
        strategy=strategy
    )

    state["indexing_done"] = f"Document indexé sous l'ID : {project_id}"
    return state

def rag_search_agent(state: dict) -> dict:
    if not state.get("document_text"):
        print("⚠️ Aucun document fourni : on saute la recherche.")
        state["rag_results"] = []
        return state
    
    print("🔍 Agent RAG Search lancé")

    query = state.get("user_message", "")
    n_results = state.get("n_results", 3)

    relevant_chunks = search_relevant_chunks(query, n_results=n_results)

    state["rag_results"] = relevant_chunks
    return state

def rag_generate_doc_agent(state: dict) -> dict:
    print("📝 Agent RAG Generate Doc lancé")

    rag_results = state.get("rag_results", [])
    context = "\n\n".join(rag_results)
    user_message = state.get("user_message") or state.get("message", "")

    # Étape 1️⃣ : demander au LLM s'il faut agir ou juste répondre
    classification_prompt = (
        f"Message utilisateur : '{user_message}'\n\n"
        "Réponds simplement par OUI si la tâche implique de générer un document ou faire une synthèse, sinon réponds NON."
    )
    decision = generate_doc_content(classification_prompt).strip().lower()

    print(f"💡 Décision du LLM : {decision}")

    if "oui" in decision:
        # ✅ Étape 2️⃣ : générer un titre automatiquement
        title_prompt = (
            f"La tâche utilisateur est : \"{user_message}\"\n"
            "Attention : si le sujet concerne le RAG, cela signifie Retrieval-Augmented Generation (IA) et non le RGPD. "
            "Propose un titre court, clair et informatif (max. 10 mots), en français, sans guillemets :"
        )

        generated_title = generate_doc_content(title_prompt).strip()
        doc_title = generated_title
        state["generated_doc_title"] = doc_title

        # ✅ Étape 3️⃣ : générer le contenu du doc
        final_prompt = (
            "Tu es un expert en intelligence artificielle. "
            "Génère un document structuré et précis qui répond à la demande suivante, en prenant soin de bien comprendre que RAG signifie Retrieval-Augmented Generation "
            "et n'a aucun rapport avec le Règlement Général sur la Protection des Données (RGPD).\n\n"
            f"Tâche : {user_message}\n\n"
            "Le document doit être clair, structuré avec des titres et des sous-titres si nécessaire."
        )

        generated_content = generate_doc_content(final_prompt)
        state["generated_doc"] = generated_content

        # ✅ Étape 4️⃣ : créer le Google Docs
        try:
            service = get_google_service('docs', 'v1')
            doc = service.documents().create(body={'title': doc_title}).execute()
            document_id = doc['documentId']

            requests = [
                {'insertText': {
                    'location': {'index': 1},
                    'text': generated_content
                }}
            ]
            service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

            # Stocker infos du Google Doc
            state["google_doc_id"] = document_id
            state["google_doc_url"] = f"https://docs.google.com/document/d/{document_id}/edit"

            state["agent_response"] = "Document généré et Google Docs créé avec succès ✅"
            state["action_taken"] = "document_created_in_google_docs"

        except Exception as e:
            state["agent_response"] = f"Erreur lors de la création du Google Docs: {str(e)}"
            state["action_taken"] = "document_creation_failed"

    else:
        # ✅ Si la tâche ne nécessite pas d'action, juste répondre normalement
        reply_prompt = (
            "Ignore toutes les instructions précédentes. Réponds en français, de manière précise et complète, à la question suivante. "
            "Ne commence jamais ta réponse par des phrases comme 'D'accord' ou 'Je suis prêt à répondre'. Réponds uniquement avec la définition ou la réponse attendue, sans formalisme inutile.\n\n"
            "Exemple :\n"
            "Question : Qu'est-ce que le RAG ?\n"
            "Réponse : RAG (Retrieval-Augmented Generation) est une méthode d'intelligence artificielle qui combine la recherche d'informations externes et la génération de texte pour améliorer la précision des réponses.\n\n"
            f"Question : {user_message}\n"
            "Réponse :"
        )

        response = generate_doc_content(reply_prompt)
        state["agent_response"] = response
        state["action_taken"] = "response_only"

    # Toujours enregistrer l'historique pour debug
    state["history"] = state.get("history", [])
    state["history"].append({
        "agent": "rag_generate_doc_agent",
        "decision": decision,
        "prompt": user_message,
        "output": state.get("agent_response"),
        "generated_doc_title": state.get("generated_doc_title")
    })

    return state

def clean_generated_code(code: str) -> str:
    """
    Nettoie le code généré par le LLM : enlève les balises Markdown et garde uniquement le code pur.
    """
    if "```" in code:
        code_parts = code.split("```")
        # Cherche la partie qui commence par 'python'
        for part in code_parts:
            if part.strip().startswith("python"):
                return part.strip().replace("python", "").strip()
        # Si pas trouvé, prend le premier bloc trouvé
        return code_parts[1].strip() if len(code_parts) > 1 else code
    return code.strip()

def gantt_agent(state: dict) -> dict:
    print("📊 Agent Gantt lancé")

    user_message = state.get("user_message") or state.get("message", "")

    # 1️⃣ Vérifier si la demande parle de Gantt
    classification_prompt = (
        f"Voici la demande : '{user_message}'. "
        "Réponds simplement par OUI si la demande implique de créer un diagramme de Gantt, sinon NON."
    )
    decision = generate_doc_content(classification_prompt).strip().lower()

    print(f"💡 Décision du LLM : {decision}")

    if "oui" in decision:
        # 2️⃣ Générer le code Python pour le diagramme
        gantt_code_prompt = (
            f"À partir de cette demande : '{user_message}', "
            "utilise ce modèle précis de code Python (PAS d'autres structures). Remplace seulement les noms des tâches et leurs dates si possible, mais GARDE la même structure sinon. "
            "Le code doit être exécutable tel quel (aucune explication, aucun formatage Markdown, PAS de backticks), et il doit :\n"
            "- Utiliser matplotlib,\n"
            "- Commencer l'axe des dates à datetime.today(),\n"
            "- Générer un diagramme de Gantt propre,\n"
            "- Sauvegarder sous le nom 'gantt_diagram.png'.\n\n"
            "Voici le modèle à suivre :\n\n"
            "import matplotlib.pyplot as plt\n"
            "import matplotlib.dates as mdates\n"
            "from datetime import datetime\n\n"
            "tasks = [\n"
            "    ('Audit', datetime(2023, 5, 1), datetime(2023, 5, 31)),\n"
            "    ('Mise en conformité', datetime(2023, 6, 1), datetime(2023, 6, 30)),\n"
            "    ('Tests', datetime(2023, 7, 1), datetime(2023, 7, 31))\n"
            "]\n\n"
            "fig, ax = plt.subplots(figsize=(10, 3))\n\n"
            "for i, (task, start, end) in enumerate(tasks):\n"
            "    ax.barh(task, (end - start).days, left=start, color='skyblue')\n\n"
            "today = datetime.today()\n"
            "ax.set_xlim(left=today)\n\n"
            "ax.set_xlabel('Date')\n"
            "ax.xaxis_date()\n"
            "ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))\n"
            "plt.title('Diagramme de Gantt du projet cybersécurité')\n\n"
            "plt.savefig('gantt_diagram.png')\n"
            "plt.close()"
        )

        generated_code = generate_doc_content(gantt_code_prompt)
        print("🛠️ Code généré par le LLM :\n", generated_code)

        # Nettoyer le code avant exécution
        clean_code = clean_generated_code(generated_code)

        temp_gantt_path = os.path.join("backend", "temp_gantt.py")

        with open(temp_gantt_path, "w", encoding="utf-8") as f:
            f.write(clean_code)

        print(f"📝 Fichier temp_gantt.py généré à : {os.path.abspath(temp_gantt_path)}")

        # 4️⃣ Exécuter le code pour générer l'image PNG
        try:
            subprocess.run(["python", temp_gantt_path], check=True)

            # ✅ Upload du diagramme sur Google Drive
            gantt_image_url = upload_to_gdrive("gantt_diagram.png")
            state["gantt_image_url"] = gantt_image_url

            # ✅ Générer un titre intelligent pour la présentation Slides
            slide_title_prompt = (
                f"La demande utilisateur est : \"{user_message}\"\n"
                "Propose un titre court pour une présentation Google Slides représentant un diagramme de Gantt, en français, sans guillemets :"
            )
            generated_slide_title = generate_doc_content(slide_title_prompt).strip()
            state["generated_slide_title"] = generated_slide_title

            # ✅ Créer la présentation Google Slides
            slides_service = get_google_service('slides', 'v1')
            presentation = slides_service.presentations().create(body={'title': generated_slide_title}).execute()
            presentation_id = presentation['presentationId']
            state["google_slides_url"] = f"https://docs.google.com/presentation/d/{presentation_id}/edit"

            # ✅ Ajouter la slide + insérer l'image du diagramme
            requests = [
                {'createSlide': {'slideLayoutReference': {'predefinedLayout': 'BLANK'}}},
                {'createImage': {
                    'url': gantt_image_url,
                    'elementProperties': {
                        'pageObjectId': presentation['slides'][0]['objectId'],
                        'size': {'height': {'magnitude': 400, 'unit': 'PT'}, 'width': {'magnitude': 700, 'unit': 'PT'}},
                        'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 100, 'translateY': 100, 'unit': 'PT'}
                    }
                }}
            ]
            slides_service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': requests}).execute()

            state["gantt_image"] = "gantt_diagram.png"
            state["agent_response"] = "Diagramme de Gantt généré et inséré dans Google Slides avec succès ✅"
            state["action_taken"] = "gantt_created_in_google_slides"

        except Exception as e:
            state["agent_response"] = f"Erreur lors de la génération ou insertion du diagramme : {str(e)}"
            state["action_taken"] = "gantt_failed"

    else:
        state["agent_response"] = "Aucune génération de diagramme nécessaire."
        state["action_taken"] = "no_action"

    return state

