import json
import os

class SessionTracker:
    def __init__(self, user_id):
        self.user_id = user_id
        self.path = f"sessions/{user_id}_session.json"
        if not os.path.exists("sessions"):
            os.makedirs("sessions")

    def store_questions(self, questions):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"questions": questions, "incorrect": []}, f, ensure_ascii=False, indent=2)

    def store_result(self, question, user_answer, correct_answer):
        try:
            with open(self.path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                if user_answer != correct_answer:
                    data.setdefault("incorrect", []).append({
                        "question": question,
                        "user_answer": user_answer,
                        "correct_answer": correct_answer
                    })
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde du résultat : {e}")

    def get_latest_results(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Impossible de charger les résultats : {e}")
            return {}

    def get_errors_by_topic(self) -> list:
        """
        Retourne une liste des questions mal répondues pour cibler les prochaines.
        """
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        incorrect = data.get("incorrect", [])
        return [item["question"] for item in incorrect if "question" in item]
