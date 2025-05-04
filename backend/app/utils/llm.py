from openai import OpenAI
import os

# Initialiser le client NVIDIA (OpenAI-compatible)
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

def generate_doc_content(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="mistralai/mistral-small-24b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=False  # ⬅️ on ne stream PAS ici pour récupérer directement la réponse complète
    )

    # Récupérer le texte généré
    content = completion.choices[0].message.content
    return content
