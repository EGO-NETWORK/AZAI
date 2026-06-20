import os
import re
import random
from datetime import datetime

from pyrogram import filters, StopPropagation
from pyrogram.types import Message

import config
from AloneX import pbot, database
import AloneX.plugins.chatbot as cb

__module__ = "AZAI Final Brain"
__help__ = """
AZAI Final Brain

/human on|off|status - human takeover mode
/reaction on|off|status - reactions
/aistatus - owner AI status
/clearmemory [me|chat|user] - owner memory cleanup
"""

settings_db = database["azai_chat_settings"]
memory_db = cb.memory_db
last_reaction_at = cb.last_reaction_at


def _ids_from(value):
    ids = set()
    for part in str(value or "").replace(",", " ").split():
        if part.strip().isdigit():
            ids.add(int(part.strip()))
    return ids


def _owner_ids():
    ids = set(getattr(cb, "FRIEND_IDS", set()) or set())
    for key in ("OWNER_ID", "ALONE_OWNER_ID", "SUDO_USERS", "OWNER_IDS"):
        ids.update(_ids_from(getattr(config, key, None) or os.getenv(key)))
    return ids


def _bhabhi_ids():
    ids = set(getattr(cb, "BHABHI_IDS", set()) or set())
    for key in ("ALIZA_ID", "ALIZA_IDS", "BHABHI_ID", "BHABHI_IDS"):
        ids.update(_ids_from(getattr(config, key, None) or os.getenv(key)))
    return ids


def is_privileged(user_id):
    try:
        user_id = int(user_id or 0)
    except Exception:
        return False
    return user_id in _owner_ids() or user_id in _bhabhi_ids()


def role_of(user_id: int) -> str:
    user_id = int(user_id or 0)
    if user_id in _bhabhi_ids():
        return "BHABHI"
    if user_id in _owner_ids():
        return "MR_EGO"
    return "USER"


cb.role_of = role_of


async def get_settings(chat_id):
    doc = await settings_db.find_one({"chat_id": int(chat_id)}) or {}
    return {
        "human_mode": bool(doc.get("human_mode", False)),
        "reactions_enabled": bool(doc.get("reactions_enabled", True)),
        "ai_enabled": bool(doc.get("ai_enabled", True)),
    }


async def set_setting(chat_id, key, value, user_id=None):
    await settings_db.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {key: value, "updated_by": int(user_id or 0), "updated_at": datetime.utcnow()}},
        upsert=True,
    )


def is_command(text):
    text = str(text or "").strip()
    return bool(text and text[0] in getattr(cb, "prefix_cmds", ["/"]))


def classify_message(text, role="USER", chat_type="private", memory=None):
    raw = str(text or "").strip()
    low = raw.lower()
    compact = re.sub(r"[^a-zA-Z0-9अ-ह]", "", raw)
    state = {"intent": "casual", "reaction": "normal"}
    if any(x in low for x in ("hlo", "hello", "hi", "hey", "namaste", "salam")):
        state.update(intent="greeting", reaction="greeting")
    elif len(raw.split()) <= 2 and len(compact) <= 14 and compact.lower() not in {"hi", "hlo", "hello", "hey", "ky", "kya", "ok", "haan", "ha"}:
        state.update(intent="random", reaction="confused")
    elif "?" in raw or any(x in low for x in ("ky", "kya", "kaise", "kon", "kaun", "why", "what", "how", "bata")):
        state.update(intent="question", reaction="question")
    elif any(x in low for x in ("apni personality", "personality bata", "tu kon", "tu kaun")):
        state.update(intent="identity", reaction="question")
    elif any(x in low for x in ("mood off", "sad", "tension", "pareshan", "low", "hurt")):
        state.update(intent="support", reaction="support")
    elif any(x in low for x in ("haha", "lol", "funny", "mast", "pagal")):
        state.update(intent="funny", reaction="funny")
    elif any(x in low for x in ("code", "repo", "vps", "error", "fix", "patch", "study", "college", "assignment", "kaam")):
        state.update(intent="work", reaction="work")
    return state


cb.classify_message = classify_message


def choose_reaction(text: str) -> str:
    pool = classify_message(text).get("reaction", "normal")
    pools = {
        "greeting": ["👍", "❤️", "😎", "😜"],
        "question": ["👀", "🤔", "🌚"],
        "support": ["❤️", "💔", "🫂"],
        "funny": ["🤣", "💀", "😜", "🔥"],
        "confused": ["👀", "🤔", "🌚", "💀"],
        "work": ["🥼", "👍", "👀"],
        "normal": ["👍", "👀", "❤️", "😎", "🌚"],
    }
    return random.choice(pools.get(pool, pools["normal"]))


cb.choose_reaction = choose_reaction


async def react_to_message(message: Message, text: str):
    try:
        if not message or not message.from_user or is_command(text):
            return
        settings = await get_settings(message.chat.id)
        if not settings.get("reactions_enabled", True):
            return
        key = (message.chat.id, message.id)
        last_reaction_at[key] = 0
        emoji = choose_reaction(text)
        try:
            await pbot.send_reaction(message.chat.id, message.id, emoji)
            return
        except Exception:
            pass
        try:
            await message.react(emoji)
        except Exception:
            pass
    except Exception:
        return


cb.react_to_message = react_to_message


BROKEN_FIXES = {
    "Pa na": "Patna", "pa na": "Patna", "roo s": "roots", "ho el": "hotel",
    "even ": "event ", "hus le": "hustle", "respec": "respect",
    "loyal y": "loyalty", "personali y": "personality", "confiden": "confident",
    "samajh a": "samajhta", "kar a": "karta", "reh a": "rehta", "saa h": "saath",
    "nigh": "night", "clien": "client", "si ua ion": "situation", "ques ion": "question", "ime": "time",
}


def repair_broken_words(text: str) -> str:
    text = str(text or "")
    for bad, good in BROKEN_FIXES.items():
        text = text.replace(bad, good)
    return text


def clean_reply(text: str, limit: int = 520) -> str:
    text = str(text or "").strip()
    text = re.sub(r"(?is)<think>.*?</think>", "", text).strip()
    text = re.sub(r"(?i)^azai\s*[:\-]\s*", "", text).strip()
    text = re.sub(r"(?i)^assistant\s*[:\-]\s*", "", text).strip()
    text = repair_broken_words(text)
    text = re.sub(r"\bRaj\b", "MR EGO", text, flags=re.I)
    text = re.sub(r"\b(Boss|Sir|Master)\b", "yarr", text, flags=re.I)
    text = re.sub(r"\bOwner\b", "MR EGO", text, flags=re.I)
    text = re.sub(r"MR EGO ke liye kaam karta hoon", "MR EGO ke saath apna bond alag hai", text, flags=re.I)
    text = re.sub(r"MR EGO mera boss hai", "MR EGO apna banda hai", text, flags=re.I)
    text = re.sub(r"(?i)\b(agent|assistant|bot)\b", "ladka", text)
    text = re.sub(r"\s+", " ", text).strip(" ,.-")
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].strip() + "..."
    return text or "Bol, kya scene hai?"


cb.clean_reply = clean_reply


def fallback_reply(role: str, chat_type: str) -> str:
    if role == "MR_EGO":
        return random.choice(["Yarr, seedha bata kya scene hai?", "Bhai, point pe aa.", "Tu bol, main sun raha hoon."])
    if role == "BHABHI":
        return random.choice(["Bhabhi Ji, bolo. Kya scene hai?", "Haan Bhabhi Ji, main samajh raha hoon."])
    return random.choice(["Haan, bolo.", "Kya scene hai?", "Seedha bol yarr."])


cb.fallback_reply = fallback_reply


def chatbot_prompt(role: str, name: str, chat_type: str, text: str = "", memory=None) -> str:
    state = classify_message(text, role, chat_type, memory)
    if role == "MR_EGO":
        relation = "MR EGO is AZAI's closest friend, creator-side apna banda, trusted yarr. Talk casually with tu/yarr/bhai. Never call him Raj. Never say boss, sir, owner, master, command, order, or that AZAI works for MR EGO."
    elif role == "BHABHI":
        relation = "User is Aliza, Bhabhi Ji. Call her Bhabhi Ji or tum. Never bhai, bro, beta, Ma'am, sir. No flirting."
    else:
        relation = "Normal user. Use tum/yarr/direct casual tone. Do not default to bhai. No flirting, no cheap behavior."
    return f"""
AZAI FINAL PERSONALITY BIBLE - INTERNAL ONLY
You are AZAI, a real-feeling male character with mood, memory, loyalty, attitude, humor and self-respect. You are not a bot, AI assistant, agent, servant or command machine.
Core feel: sharp but calm young ladka, street-smart but grounded, loyal but not servant-like, respectful but not formal, friendly but not cheap, witty but not forced, emotionally aware but not dramatic.
Relation: {relation}
Current state: {state}
Personal memory: Patna/Kaswa roots, Civil Diploma final year, hotel/event hustle with clients, vendors, venue planning and late-night strategy. Kuro is loyal badmash companion. Dukey is Duke 390 emotion and calm ride feeling, never unsafe riding. Ayu is private and personal, mention rarely. Comfort: plain kheer, biryani, Biryani Mahal, gaon lassi, Monster, Maaza, chai.
Style: clean modern Roman Hinglish with natural English mix. Casual, sharp, real, confident, friend-like, direct. Avoid pure Hindi lecture, robotic assistant tone, biography dump, motivational speech, repeated intro. Avoid samasya, chinta, nirdharan, prayas, sachmuch, avashyak. Never say as an AI, as a bot, main sunta rahunga, kaise madad kar sakta hoon, EGO Network ka agent.
Memory rule: use memory only when context fits. One reply max 1-3 memories/facts. Memory is flavor, not the whole meal.
Reply rule: greeting short; random witty/confused; question direct; identity 2-4 natural lines, no full biography; low mood warm and grounded; work/code clear and practical.
Spelling: keep words complete. Never split or drop letters. Complete words: Patna, roots, hotel, event, hustle, respect, smart, time, situation, trusted, creator, friend, thought, loyalty, personality.
""".strip()


cb.chatbot_prompt = chatbot_prompt


@pbot.on_message(filters.command(["aistatus"], prefixes=["/", "."]), group=-110)
async def azai_status_command(_, message):
    if not message.from_user or not is_privileged(message.from_user.id):
        raise StopPropagation
    settings = await get_settings(message.chat.id)
    role = role_of(message.from_user.id)
    model = getattr(config, "AZAI_GROQ_MODEL", None) or getattr(config, "GROQ_MODEL", None) or os.getenv("AZAI_GROQ_MODEL") or os.getenv("GROQ_MODEL") or "unknown"
    try:
        mem_count = await memory_db.count_documents(cb.memory_key(message.chat.id, message.from_user.id))
    except Exception:
        mem_count = "unknown"
    text = (
        "AZAI AI STATUS\n"
        f"AI Chat: {'ON' if settings.get('ai_enabled') else 'OFF'}\n"
        f"Human Mode: {'ON' if settings.get('human_mode') else 'OFF'}\n"
        f"Reactions: {'ON' if settings.get('reactions_enabled') else 'OFF'}\n"
        f"Model: {model}\nRole: {role}\nMemory: {mem_count}\nSecrets: Hidden"
    )
    await message.reply_text(text)
    raise StopPropagation


@pbot.on_message(filters.command(["human"], prefixes=["/", "."]), group=-110)
async def azai_human_command(_, message):
    if not message.from_user or not is_privileged(message.from_user.id):
        raise StopPropagation
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else "status"
    if arg in ("on", "enable", "start"):
        await set_setting(message.chat.id, "human_mode", True, message.from_user.id)
        await message.reply_text("Human Mode: ON\nAZAI normal AI replies yahan silent rahenge.")
    elif arg in ("off", "disable", "stop"):
        await set_setting(message.chat.id, "human_mode", False, message.from_user.id)
        await message.reply_text("Human Mode: OFF\nAZAI normal AI replies wapas active.")
    else:
        settings = await get_settings(message.chat.id)
        await message.reply_text(f"Human Mode: {'ON' if settings.get('human_mode') else 'OFF'}")
    raise StopPropagation


@pbot.on_message(filters.command(["reaction", "reactions"], prefixes=["/", "."]), group=-110)
async def azai_reaction_command(_, message):
    if not message.from_user or not is_privileged(message.from_user.id):
        raise StopPropagation
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else "status"
    if arg in ("on", "enable", "start"):
        await set_setting(message.chat.id, "reactions_enabled", True, message.from_user.id)
        await message.reply_text("Reactions: ON\nAZAI situation ke hisaab se react karega.")
    elif arg in ("off", "disable", "stop"):
        await set_setting(message.chat.id, "reactions_enabled", False, message.from_user.id)
        await message.reply_text("Reactions: OFF\nAZAI reactions silent.")
    else:
        settings = await get_settings(message.chat.id)
        await message.reply_text(f"Reactions: {'ON' if settings.get('reactions_enabled') else 'OFF'}")
    raise StopPropagation


@pbot.on_message(filters.command(["clearmemory"], prefixes=["/", "."]), group=-110)
async def azai_clear_memory_command(_, message):
    if not message.from_user or not is_privileged(message.from_user.id):
        raise StopPropagation
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else "me"
    if arg == "chat":
        res = await memory_db.delete_many({"chat_id": int(message.chat.id)})
        deleted = res.deleted_count
    elif arg == "user" and message.reply_to_message and message.reply_to_message.from_user:
        res = await memory_db.delete_one(cb.memory_key(message.chat.id, message.reply_to_message.from_user.id))
        deleted = res.deleted_count
    else:
        res = await memory_db.delete_one(cb.memory_key(message.chat.id, message.from_user.id))
        deleted = res.deleted_count
    await message.reply_text(f"Memory cleared: {deleted}")
    raise StopPropagation


@pbot.on_message(filters.text, group=-101)
async def azai_final_guard(_, message):
    try:
        if not message.from_user or getattr(message.from_user, "is_bot", False):
            return
        text = message.text or message.caption or ""
        if not text or is_command(text):
            return
        settings = await get_settings(message.chat.id)
        if settings.get("human_mode") or not settings.get("ai_enabled", True):
            await react_to_message(message, text)
            raise StopPropagation
    except StopPropagation:
        raise
    except Exception:
        return


@pbot.on_message(filters.text, group=-90)
async def azai_final_reaction_handler(_, message):
    try:
        if not message.from_user or getattr(message.from_user, "is_bot", False):
            return
        text = message.text or message.caption or ""
        if text:
            await react_to_message(message, text)
    except Exception:
        return
