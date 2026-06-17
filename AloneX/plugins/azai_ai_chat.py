import os
import time
import re
import unicodedata

import aiohttp
from telethon import Button, events

from AloneX import BOT_USERNAME, database, font as panel_font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, GROQ_API_KEY, OWNER_ID

AZAI_BOT_USERNAME = "Urxazaibot"
GROQ_MODEL = os.getenv("AZAI_GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
AI_COOLDOWN_SECONDS = 3
MEMORY_LIMIT = 8

last_reply_at = {}
memory_db = database["azai_ai_memory"]
profile_db = database["azai_profile_modes"]

BOY_NAMES = {"raj", "rahul", "aman", "rohit", "sahil", "arjun", "aryan", "vivek", "mohit", "mr", "ego", "egoisticxprime", "mrego", "prime"}
GIRL_NAMES = {"aliza", "ayesha", "priya", "neha", "anjali", "rani", "muskan", "isha", "sana", "fatima", "zoya"}
SOFT_WORDS = {"mood off", "tension", "akela", "overthinking", "overthink", "low", "udaas"}
POSITIVE_WORDS = {"thanks", "thank", "mast", "nice", "good", "op", "smart", "strong", "sahi"}
ROUGH_WORDS = {"gali", "rough", "bad", "bakwas", "faltu", "mc", "bc", "madar", "chod", "chuti", "gand", "bhos", "lawd"}
ACTION_TAG_RE = re.compile(r"\*[^*]{1,100}\*|\([^)]{1,100}\)")


def env_int(name: str, default: int = 0) -> int:
    try:
        return int(os.getenv(name, str(default)) or default)
    except Exception:
        return default


def owner_ids() -> set[int]:
    ids = set()
    for key in ("OWNER_ID", "ALONE_OWNER_ID", "SUDO_USERS"):
        raw = os.getenv(key, "")
        for part in str(raw).replace(",", " ").split():
            if part.strip().isdigit():
                ids.add(int(part.strip()))
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


BHABHI_IDS = set()
for key in ("ALIZA_ID", "BHABHI_ID"):
    raw = os.getenv(key, "")
    for part in str(raw).replace(",", " ").split():
        if part.strip().isdigit():
            BHABHI_IDS.add(int(part.strip()))


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


def first_name_from_user(user) -> str:
    name = getattr(user, "first_name", "") or ""
    username = getattr(user, "username", "") or ""
    parts = re.sub(r"[^a-zA-Z]+", " ", f"{name} {username}").lower().strip().split()
    return parts[0] if parts else ""


def guess_profile_mode(user) -> str:
    key = first_name_from_user(user)
    if key in BOY_NAMES:
        return "male"
    if key in GIRL_NAMES:
        return "female"
    return "unknown"


async def stored_profile_mode(user_id: int) -> str | None:
    row = await profile_db.find_one({"user_id": int(user_id)}) or {}
    return row.get("mode")


async def save_profile_mode(user_id: int, mode: str):
    await profile_db.update_one({"user_id": int(user_id)}, {"$set": {"user_id": int(user_id), "mode": mode, "updated_at": int(time.time())}}, upsert=True)


def user_role(user_id: int) -> str:
    if int(user_id) in owner_ids():
        return "OWNER"
    if int(user_id) in BHABHI_IDS:
        return "BHABHI"
    return "USER"


def should_reply_in_group(text: str, mentioned: bool, replied_to_bot: bool) -> bool:
    text_low = (text or "").lower()
    if mentioned or replied_to_bot:
        return True
    triggers = ["azai", "azaii", "azai bot", clean_bot_username().lower()]
    return any(trigger in text_low for trigger in triggers)


def profile_rule(role: str, mode: str | None) -> str:
    if role == "OWNER":
        return "USER IS MR EGO. DIRECT OWNER TONE. NEVER CALL HIM BHABHI. NO SERVANT TONE."
    if role == "BHABHI":
        return "USER IS ALIZA. SAY BHABHI JI OR MAAM ONLY WHEN NATURAL. NEVER CALL HER BHAI. RESPECTFUL BUT NORMAL."
    if mode == "male":
        return "USER IS MALE. USE BHAI/BRO TONE."
    if mode == "female":
        return "USER IS FEMALE. RESPECTFUL NORMAL TONE. DO NOT OVERUSE MAAM."
    return "USER UNKNOWN. STAY CLEAN, SHORT, NATURAL."


def system_prompt(role: str, first_name: str | None, mode: str | None) -> str:
    return (
        "YOU ARE AZAI, EGO NETWORK KA REAL-FEEL MALE CHARACTER. "
        "REPLY IN NORMAL CAPITAL HINGLISH. NO STYLISH UNICODE FONT. NO PURE HINDI. NO SHUDH HINDI WORDS. "
        "NO ROLEPLAY ACTIONS. NO STAGE DIRECTIONS. NO VIRTUAL ACTING. "
        "NO SERVANT/GULAM TONE. RESPECTFUL DOES NOT MEAN SERVANT. "
        "FOR GIRLS: RESPECTFUL, NORMAL, CLEAN, SHORT. DO NOT SAY MAAM IN EVERY LINE. "
        "USE PATNA/BIHAR SIDE COOL LADKA VIBE. SLIGHT SARCASM OK. "
        "UNDERSTAND SLANG AND ABUSE, BUT DO NOT REPLY WITH ABUSE. "
        "AVOID HOON-HOON STYLE. USE SIMPLE HINGLISH LIKE: SCENE KYA HAI, KAAM BATA, BOL, KARTE HAIN. "
        "DO NOT CALL YOURSELF AI, BOT, ASSISTANT, OR AGENT IN PUBLIC REPLIES. "
        f"{profile_rule(role, mode)} USER FIRST NAME IF USEFUL: {first_name or 'USER'}."
    )


def _plain_text(text: str) -> str:
    text = str(text or "")
    text = ACTION_TAG_RE.sub("", text)
    text = re.sub(r"\bvirtual\b", "", text, flags=re.I)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    bad = ["MOTHER TONGUE", "SANTUSHT", "SERIOUS TONE", "SMILES", "LOOKS CONCERNED", "MAIN AAPKE SAATH", "MAIN HINDI MEIN"]
    for item in bad:
        text = text.replace(item, "")
    text = text.replace("HOON HOON", "HU")
    text = text.replace("HOON.", "HU.")
    return text.strip()


def fallback_reply(role: str, mode: str | None) -> str:
    if not has_key(groq_key()):
        if role == "OWNER":
            return "SIR, AI LINK OFFLINE HAI. CORE SYSTEM ACTIVE HAI."
        if role == "BHABHI":
            return "BHABHI JI, AI LINK OFFLINE HAI. COMMANDS READY HAIN."
        if mode == "female":
            return "SCENE CLEAR BATAO, HELP KAR DUNGA."
        return "BHAI, AI LINK OFFLINE HAI. COMMANDS ACTIVE HAIN."
    return "NETWORK BLINK HUA. EK BAAR PHIR BHEJ."


def trim_reply(text: str) -> str:
    text = _plain_text(text)
    if len(text) > 220:
        text = text[:220].rsplit(" ", 1)[0] + "..."
    return (text or "BHAI, SCENE CLEAR BOL.").upper()


def memory_key(chat_id: int, user_id: int) -> dict:
    return {"chat_id": int(chat_id), "user_id": int(user_id)}


async def load_memory(chat_id: int, user_id: int) -> list[dict]:
    data = await memory_db.find_one(memory_key(chat_id, user_id))
    turns = data.get("turns", []) if data else []
    safe_turns = []
    for turn in turns[-MEMORY_LIMIT:]:
        role = turn.get("role")
        content = str(turn.get("content", ""))[:500]
        if role in {"user", "assistant"} and content:
            safe_turns.append({"role": role, "content": content})
    return safe_turns


async def save_memory(chat_id: int, user_id: int, user_text: str, bot_text: str):
    key = memory_key(chat_id, user_id)
    data = await memory_db.find_one(key)
    turns = data.get("turns", []) if data else []
    turns.append({"role": "user", "content": str(user_text or "")[:500]})
    turns.append({"role": "assistant", "content": str(bot_text or "")[:500]})
    turns = turns[-MEMORY_LIMIT:]
    await memory_db.update_one(key, {"$set": {**key, "turns": turns, "updated_at": int(time.time())}}, upsert=True)


async def ask_groq(user_text: str, role: str, first_name: str | None, mode: str | None, memory: list[dict] | None = None) -> str | None:
    key = groq_key()
    if not has_key(key):
        return None

    messages = [{"role": "system", "content": system_prompt(role, first_name, mode)}]
    if memory:
        messages.extend(memory[-MEMORY_LIMIT:])
    messages.append({"role": "user", "content": user_text[:1400]})

    payload = {"model": GROQ_MODEL, "messages": messages, "temperature": 0.65, "max_tokens": 80}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_ENDPOINT, json=payload, headers=headers, timeout=25) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception:
        return None


async def replied_to_me(event) -> bool:
    try:
        reply = await event.get_reply_message()
        if not reply:
            return False
        sender = await reply.get_sender()
        return bool(sender and getattr(sender, "bot", False) and (sender.username or "").lower() == clean_bot_username().lower())
    except Exception:
        return False


def reaction_for(text: str) -> str | None:
    low = (text or "").lower()
    if any(x in low for x in SOFT_WORDS):
        return "❤️"
    if any(x in low for x in ROUGH_WORDS):
        return "😐"
    if any(x in low for x in POSITIVE_WORDS):
        return "🔥"
    return None


async def react_safe(event, emoji: str | None):
    if not emoji:
        return
    try:
        await event.message.react(emoji)
    except Exception:
        pass


async def ask_profile_mode(event):
    buttons = [[
        Button.inline(panel_font("Bhai Mode"), b"azai_ai_profile_male"),
        Button.inline(panel_font("Ma'am Mode"), b"azai_ai_profile_female"),
    ], [
        Button.inline(panel_font("Neutral"), b"azai_ai_profile_neutral"),
        Button.inline(panel_font("Skip"), b"azai_ai_profile_skip"),
    ]]
    await event.reply("PROFILE MODE CLEAR NAHI HAI. TONE LOCK KARNE KE LIYE MODE CHOOSE KAR DO.", buttons=buttons)
    raise events.StopPropagation


async def profile_mode_callback(event):
    sender = await event.get_sender()
    if not sender:
        return
    data = (event.data or b"").decode()
    mode = data.replace("azai_ai_profile_", "")
    if mode == "skip":
        mode = "neutral"
    await save_profile_mode(int(sender.id), mode)
    label = {"male": "Bhai Mode", "female": "Ma'am Mode", "neutral": "Neutral"}.get(mode, "Neutral")
    await event.edit(panel_font(f"Locked: {label}"))
    raise events.StopPropagation


async def ai_chat_handler(event):
    if event.fwd_from:
        return
    text = (event.raw_text or "").strip()
    if not text or is_command(text):
        return

    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    role = user_role(sender.id)
    is_private = bool(event.is_private)
    mentioned = f"@{clean_bot_username().lower()}" in text.lower()
    reply_to_bot = False if is_private else await replied_to_me(event)

    if not is_private and not should_reply_in_group(text, mentioned, reply_to_bot):
        return

    await react_safe(event, reaction_for(text))

    cd_key = (event.chat_id, sender.id)
    now = time.time()
    if last_reply_at.get(cd_key, 0) + AI_COOLDOWN_SECONDS > now:
        return
    last_reply_at[cd_key] = now

    if mentioned:
        text = text.replace(f"@{clean_bot_username()}", "").replace(f"@{clean_bot_username().lower()}", "").strip() or "hello"

    mode = None
    if role == "USER":
        mode = await stored_profile_mode(sender.id)
        if not mode:
            guessed = guess_profile_mode(sender)
            if guessed == "unknown":
                await ask_profile_mode(event)
                return
            mode = guessed

    memory = await load_memory(event.chat_id, sender.id)
    reply = await ask_groq(text, role, getattr(sender, "first_name", None), mode, memory)
    plain_reply = None
    if not reply:
        reply = fallback_reply(role, mode)
    else:
        plain_reply = trim_reply(reply)
        reply = plain_reply

    try:
        await event.reply(reply)
    except Exception:
        await event.respond(reply)

    if plain_reply:
        await save_memory(event.chat_id, sender.id, text, plain_reply)

    raise events.StopPropagation


if "azai_ai_chat" not in tbot.handlers_loaded:
    tbot.add_event_handler(profile_mode_callback, events.CallbackQuery(pattern=b"^azai_ai_profile_"))
    tbot.add_event_handler(ai_chat_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_ai_chat")
