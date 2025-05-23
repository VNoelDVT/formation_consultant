import json
import os
import re
from datetime import datetime

class SessionTracker:
    def __init__(self, user_id):
        self.user_id = user_id
        self.base_path = f"sessions"
        os.makedirs(self.base_path, exist_ok=True)

    def get_new_session_id(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{self.user_id}_{timestamp}"

    def store_questions(self, questions):
        session_id = self.get_new_session_id()
        path = os.path.join(self.base_path, f"{session_id}_questions.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2)
        return session_id

    def store_user_responses(self, session_id, responses):
        path = os.path.join(self.base_path, f"{session_id}_responses.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2)

    def store_correct_answers(self, session_id, correct_answers):
        path = os.path.join(self.base_path, f"{session_id}_truth.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(correct_answers, f, indent=2)

    def store_results(self, session_id, result_summary):
        path = os.path.join(self.base_path, f"{session_id}_results.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result_summary, f, indent=2)

    def get_latest_results(self):
        # Optionally fetch the latest _results.json file
        files = [f for f in os.listdir(self.base_path) if f.endswith("_results.json")]
        if not files:
            return {}
        latest_file = sorted(files)[-1]
        with open(os.path.join(self.base_path, latest_file), "r", encoding="utf-8") as f:
            return json.load(f)

    def get_errors_by_topic(self):
        # Placeholder for actual topic-based error tracking
        return []
    
    def get_last_session_id(self):
        if not os.path.exists(self.base_path):
            return None

        print(self.base_path)
        files = os.listdir(self.base_path)

        # Filtrer uniquement les fichiers questions pour cet utilisateur
        pattern = rf"{self.user_id}_questions_{self.user_id}_(\d+)\.json"
        question_files = [f for f in files if re.match(pattern, f)]

        if not question_files:
            return None

        # Extraire les timestamps et trier
        timestamps = []
        for f in question_files:
            match = re.match(pattern, f)
            if match:
                timestamps.append(match.group(1))

        if not timestamps:
            return None

        timestamps.sort()
        latest_timestamp = timestamps[-1]
        return f"{self.user_id}_{latest_timestamp}"
    
    def save_user_answers(self, session_id, answers: list):
        """
        Sauvegarde les réponses utilisateur dans un fichier.
        """
        path = os.path.join(self.base_path, f"{self.user_id}_answers_{session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"answers": answers}, f, ensure_ascii=False, indent=2)


