import os

try:
    from config import GROQ_API_KEY
except Exception:
    GROQ_API_KEY = "0"


def _azai_groq_key() -> str:
    return GROQ_API_KEY or os.getenv("GROQ_API_KEY") or os.getenv("GRQI_API_KEY") or os.getenv("GQRI_API_KEY") or "0"


try:
    import AloneX.plugins.azai_ai_chat as azai_ai_chat

    azai_ai_chat.groq_key = _azai_groq_key
except Exception:
    pass
