"""AZAI AI chat compatibility shim.

AI chat/Groq runtime is disabled on the stable cleanup branch.
This file only preserves import compatibility for older leftover plugins.
"""

has_key = False
groq_key = ""
system_prompt = ""
CHAT_IDS = set()


def fallback_reply(*args, **kwargs):
    return ""


async def add_chat(chat_id):
    try:
        CHAT_IDS.add(int(chat_id))
    except Exception:
        pass


async def remove_chat(chat_id):
    try:
        CHAT_IDS.discard(int(chat_id))
    except Exception:
        pass


async def reset_chat_chatbot(chat_id):
    try:
        CHAT_IDS.discard(int(chat_id))
    except Exception:
        pass


async def chatbot_handler(*args, **kwargs):
    return None
