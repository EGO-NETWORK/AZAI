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
