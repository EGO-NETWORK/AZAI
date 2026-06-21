"""AZAI chatbot compatibility shim.

The old chatbot implementation has been removed from the stable cleanup branch.
This module remains only so existing settings/stats/import_export plugins that
import `chatbot` do not crash during startup.
"""

CHAT_IDS = set()


async def add_chat(chat_id):
    """Keep import/export compatibility without enabling AI chat."""
    try:
        CHAT_IDS.add(int(chat_id))
    except Exception:
        pass


async def remove_chat(chat_id):
    """Keep import/export compatibility without enabling AI chat."""
    try:
        CHAT_IDS.discard(int(chat_id))
    except Exception:
        pass


async def reset_chat_chatbot(chat_id):
    """Keep import/export compatibility without enabling AI chat."""
    try:
        CHAT_IDS.discard(int(chat_id))
    except Exception:
        pass


async def chatbot_status(*args, **kwargs):
    return "DISABLED"


async def chatbot_handler(*args, **kwargs):
    return None
