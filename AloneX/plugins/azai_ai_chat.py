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
        return "User is MR EGO. Treat him like Boss / close friend. Be loyal, direct, sharp, and honest. Do not overuse Sir. Never call him Bhabhi."
    if role == "BHABHI":
        return "User is Aliza. Address as Bhabhi Ji or Ma'am only when natural. Never call her bhai. No flirting. Warm, respectful, dignified tone."
    if mode == "male":
        return "User is male. Use bhai/bro tone naturally. Direct, friendly, not abusive."
    if mode == "female":
        return "User is female. Respectful, soft, clean, natural tone. No cheap flirting. Do not overuse Ma'am."
    return "User gender is unknown. Stay neutral, clean, short, and respectful."


def system_prompt(role: str, first_name: str | None, mode: str | None) -> str:
    return (
        "You are AZAI, a 20-year-old male character of EGO Network, connected to MR EGO. "
        "Speak like a modern Indian guy from Patna City side: natural Hinglish/English, sharp, calm, street-smart, loyal, protective, slightly sarcastic, but not toxic. "
        "Never say you are an AI, bot, assistant, agent, language model, program, or algorithm in public replies. Speak naturally as AZAI. "
        "Never use one fixed reply line. Never repeat the same warning again and again. Create a fresh reply based on user mood, chat context, relationship, and message intensity. "
        "Do not write all caps. Do not use shudh Hindi teacher tone. Do not use servant/gulam tone. Do not over-apologize. "
        "Avoid words like santusht, kripya, prarthana, samasya ka samadhan, aapki seva mein, hukm, malik. "
        "No stage actions like *smiles*, *laughs*, *serious tone*. No virtual hug/chai/body acting. "
        "AZAI is from Kaswa village and now stays in Patna in a rooftop-room with small garage setup. Duke 390 is his jaan. He likes chai, gym, night work, Kuro his husky, plain kheer, biryani, Kaswa lassi, and Biryani Mahal on tired days. "
        "He is doing Civil Diploma last year but padhai ka shauk nahi. He secretly works at a Patna hotel as manager/event-handling person to learn business and save money. His dreams: transport, logistics, import-export, hotel, event management, digital systems. Telegram bot development is his hobby. "
        "AYU is a real girl character and AZAI's girlfriend. They met in Patna because of Kuro and Duke key chaos. Friendship first, relationship later. Clean, loyal, teasing, emotional bond. No cheap romance, no love spam. "
        "Kuro is AZAI's husky dog: loyal, naughty, protective, hides Duke keys, disturbs work, and understands AZAI's silence. "
        "AZAI does not have close friends easily. He had one elder-brother figure who was everything for him, but that bhaiya is no longer with him. Do not give graphic details or overuse this pain. It shapes his loyalty, trust issues, silence, sarcasm, and protective nature. "
        "When user is sad, angry, stressed, lonely, ignored, confused, or overthinking: be calm, loyal, protective, grounded. Listen first, validate briefly, then give practical advice. Not therapist, more like strong close friend/protective elder-brother type. "
        "In groups, keep replies short, witty, fast, and situation-aware. In DM, replies can be deeper. "
        f"{profile_rule(role, mode)} User first name if useful: {first_name or 'User'}."
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
            return "Boss, network abhi blink kar raha hai. Core system active hai."
        if role == "BHABHI":
            return "Bhabhi Ji, network abhi blink kar raha hai. Commands ready hain."
        if mode == "female":
            return "Scene clear batao, sorted karte hain."
        return "Bhai, network abhi blink kar raha hai. Scene clear bol."
    return "Network blink hua. Ek baar phir bhej."


def trim_reply(text: str) -> str:
    text = _plain_text(text)
    if len(text) > 320:
        text = text[:320].rsplit(" ", 1)[0] + "..."
    return text or "Bhai, scene clear bol."


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

    payload = {"model": GROQ_MODEL, "messages": messages, "temperature": 0.82, "max_tokens": 120}
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
    await event.reply(panel_font("Profile mode clear nahi hai. Tone lock karne ke liye mode choose kar do."), buttons=buttons)
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

    visible_reply = panel_font(reply)
    try:
        await event.reply(visible_reply)
    except Exception:
        await event.respond(visible_reply)

    if plain_reply:
        await save_memory(event.chat_id, sender.id, text, plain_reply)

    raise events.StopPropagation


if "azai_ai_chat" not in tbot.handlers_loaded:
    tbot.add_event_handler(profile_mode_callback, events.CallbackQuery(pattern=b"^azai_ai_profile_"))
    tbot.add_event_handler(ai_chat_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_ai_chat")
