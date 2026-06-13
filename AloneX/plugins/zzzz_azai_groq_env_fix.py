import os

from AloneX.plugins import azai_ai_chat as chat


def fixed_groq_key() -> str:
    return os.getenv("GROQ_API_KEY") or os.getenv("GRQI_API_KEY") or os.getenv("GQRI_API_KEY") or "0"


chat.GROQ_API_KEY = fixed_groq_key()
chat.groq_key = fixed_groq_key
