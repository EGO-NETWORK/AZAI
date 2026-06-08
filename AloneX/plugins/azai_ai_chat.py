import os
import time

import aiohttp
from telethon import events

from AloneX import BOT_USERNAME, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, GROQ_API_KEY, OWNER_ID

AZAI_BOT_USERNAME = "Urxazaibot"
GROQ_MODEL = os.getenv("AZAI_GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
AI_COOLDOWN_SECONDS = 3

last_reply_at = {}


def env_int(name: str, default: int = 0) -> int:
    try:
        return int(os.getenv(name, str(default)) or default)
    except Exception:
        return default


def owner_ids() -> set[int]:
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


ALIZA_ID = env_int("ALIZA_ID", env_int("BHABHI_ID", 0))


def clean_bot_username() -> str:
    username = str(BOT_USERNAME or AZAI_BOT_USERNAME).replace("@", "").strip()
    if not username or username.lower() in {"azai", "oxnybot", "eiko"}:
        username = AZAI_BOT_USERNAME
    return username


def groq_key() -> str:
    return GROQ_API_KEY or os.getenv("GROQ_API_KEY") or os.getenv("GQRI_API_KEY") or "0"


def has_key(value: str) -> bool:
    value = str(value or "").strip()
    return bool(value and value.lower() not in {"0", "none", "null", "false", "your_groq_key", "your_groq_api_key"})


def is_command(text: str) -> bool:
    text = (text or "").strip()
    return bool(text and text[0] in prefix_cmds)


def user_role(user_id: int) -> str:
    if user_id in owner_ids():
        return "OWNER"
    if ALIZA_ID and user_id == ALIZA_ID:
        return "BHABHI"
    return "USER"


def should_reply_in_group(text: str, mentioned: bool, replied_to_bot: bool) -> bool:
    text_low = (text or "").lower()
    if mentioned or replied_to_bot:
        return True
    triggers = ["azai", "azaii", "azai bot", clean_bot_username().lower()]
    return any(trigger in text_low for trigger in triggers)
