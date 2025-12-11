import os
from dotenv import load_dotenv
from openai import OpenAI

# Toujours charger le .env situé dans backend/
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Initialiser le client NVIDIA (OpenAI-compatible)
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="nvapi-..."
)

def generate_content(prompt: str) -> str:
    completion = client.chat.completions.create(
    model="mistralai/mistral-small-24b-instruct",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024,
    stream=False  # ✅ Pour avoir la réponse complète d'un coup
    )
    return completion.choices[0].message.content
