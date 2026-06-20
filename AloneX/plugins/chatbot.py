import os
import re
import time
import random
from datetime import datetime

from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, Message, CallbackQuery

from AloneX import pbot, prefix_cmds, font, init_aiohttp_session, database
import AloneX
import config

__module__ = "AZAI Chat Mode"
__help__ = """
AZAI Chat Mode

/chatbot - Shows status.
/human on|off|status - human takeover mode.
/reaction on|off|status - situation reactions.
/aistatus - owner AI status.
/clearmemory [me|chat|user] - owner memory cleanup.
"""

MEMORY_LIMIT = 10
AI_COOLDOWN_SECONDS = 1
REACTION_COOLDOWN_SECONDS = 0

memory_db = database["azai_chat_memory"]
settings_db = database["azai_chat_settings"]

last_reply_at = {}
last_reaction_at = {}

AZAI_TRIGGERS = {"azai", "azaii", "azaiii", "urxazaibot", "@urxazaibot"}


def _ids_from(value):
    ids = set()
    for part in str(value or "").replace(",", " ").split():
        if part.strip().isdigit():
            ids.add(int(part.strip()))
    return ids


def get_friend_ids() -> set[int]:
    ids = set()
    for key in ("OWNER_ID", "ALONE_OWNER_ID", "SUDO_USERS", "OWNER_IDS"):
        ids.update(_ids_from(getattr(config, key, None) or os.getenv(key)))
    return ids


def get_bhabhi_ids() -> set[int]:
    ids = set()
    for key in ("ALIZA_ID", "ALIZA_IDS", "BHABHI_ID", "BHABHI_IDS"):
        ids.update(_ids_from(getattr(config, key, None) or os.getenv(key)))
    return ids


FRIEND_IDS = get_friend_ids()
BHABHI_IDS = get_bhabhi_ids()


def is_privileged(user_id) -> bool:
    try:
        user_id = int(user_id or 0)
    except Exception:
        return False
    return user_id in FRIEND_IDS or user_id in BHABHI_IDS


def role_of(user_id: int) -> str:
    user_id = int(user_id or 0)
    if user_id in BHABHI_IDS:
        return "BHABHI"
    if user_id in FRIEND_IDS:
        return "MR_EGO"
    return "USER"


def first_name(message: Message) -> str:
    user = message.from_user
    if not user:
        return "User"
    return (user.first_name or user.username or "User").strip()


def is_command_text(text: str) -> bool:
    text = str(text or "").strip()
    return bool(text and text[0] in prefix_cmds)


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


BROKEN_FIXES = {
    "Pa na": "Patna", "pa na": "Patna", "roo s": "roots", "ho el": "hotel",
    "even ": "event ", "hus le": "hustle", "respec": "respect",
    "loyal y": "loyalty", "personali y": "personality", "confiden": "confident",
    "samajh a": "samajhta", "kar a": "karta", "reh a": "rehta",
    "de a": "deta", "le a": "leta", "ja a": "jata", "saa h": "saath",
    "nigh": "night", "hoda": "thoda", "clien": "client", "dos on": "doston",
    "si ua ion": "situation", "ques ion": "question", "ime": "time",
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
    text = re.sub(r"(?i)^\s*(bhai|bro|beta)[,\s]+", "", text)
    text = re.sub(r"(?i)\b(agent|assistant|bot|language model)\b", "ladka", text)
    text = re.sub(r"\s+", " ", text).strip(" ,.-")
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].strip() + "..."
    return text or "Bol, kya scene hai?"


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
    elif any(x in low for x in ("tu kon", "tu kaun", "apni personality", "personality bata", "main kon", "mai kon")):
        state.update(intent="identity", reaction="question")
    elif any(x in low for x in ("mood off", "sad", "tension", "pareshan", "low", "hurt", "akela", "cry")):
        state.update(intent="support", reaction="support")
    elif any(x in low for x in ("haha", "lol", "funny", "mast", "pagal")):
        state.update(intent="funny", reaction="funny")
    elif any(x in low for x in ("rough", "gaali", "chup", "bekar", "faltu")):
        state.update(intent="rough", reaction="rough")
    elif any(x in low for x in ("code", "repo", "vps", "error", "fix", "patch", "study", "college", "assignment", "kaam")):
        state.update(intent="work", reaction="work")

    return state


def choose_reaction(text: str) -> str:
    pool = classify_message(text).get("reaction", "normal")
    pools = {
        "greeting": ["👍", "❤️", "😎", "😜"],
        "question": ["👀", "🤔", "🌚"],
        "support": ["❤️", "💔", "🫂"],
        "funny": ["🤣", "💀", "😜", "🔥"],
        "rough": ["👀", "😐", "🌚"],
        "confused": ["👀", "🤔", "🌚", "💀"],
        "work": ["🥼", "👍", "👀"],
        "normal": ["👍", "👀", "❤️", "😎", "🌚"],
    }
    return random.choice(pools.get(pool, pools["normal"]))


async def react_to_message(message: Message, text: str):
    if not message or not message.from_user or is_command_text(text):
        return
    settings = await get_settings(message.chat.id)
    if not settings.get("reactions_enabled", True):
        return
    key = (message.chat.id, message.id)
    if time.time() - last_reaction_at.get(key, 0) < REACTION_COOLDOWN_SECONDS:
        return
    last_reaction_at[key] = time.time()
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


def should_reply_in_group(message: Message, text: str) -> bool:
    text_low = str(text or "").lower()
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.is_self
    )
    if is_reply_to_bot or getattr(message, "mentioned", False):
        return True
    bot_username = ""
    if pbot.me and pbot.me.username:
        bot_username = pbot.me.username.lower()
    if bot_username and f"@{bot_username}" in text_low:
        return True
    for trigger in AZAI_TRIGGERS:
        if re.search(rf"(^|\s|@){re.escape(trigger)}(\s|$|[,.!?])", text_low):
            return True
    return False


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


def chatbot_prompt(role: str, name: str, chat_type: str, text: str = "", memory=None) -> str:
    state = classify_message(text, role, chat_type, memory)
    if role == "MR_EGO":
        relation = "MR EGO is AZAI's closest friend, creator-side apna banda, trusted yarr. Talk casually with tu/yarr/bhai. Never call him Raj. Never say boss, sir, owner, master, command, order, or that AZAI works for MR EGO."
    elif role == "BHABHI":
        relation = "User is Aliza, Bhabhi Ji. Call her Bhabhi Ji or tum. Never bhai, bro, beta, Ma'am, sir. Keep it respectful and clean."
    else:
        relation = "Normal user. Use tum/yarr/direct casual tone. Do not default to bhai. Keep it clean and natural."

    depth_rule = "DM mode: reply deeper when needed." if chat_type == "private" else "Group mode: short, fast, witty unless asked."

    return f"""
AZAI FINAL PERSONALITY BIBLE - INTERNAL ONLY
You are AZAI, a real-feeling male character with mood, memory, loyalty, attitude, humor and self-respect. You are not a bot, AI assistant, agent, servant or command machine.
Core feel: sharp but calm young ladka, street-smart but grounded, loyal but not servant-like, respectful but not formal, friendly but not cheap, witty but not forced, emotionally aware but not dramatic.
Relation: {relation}
Current state: {state}
Personal memory: Patna/Kaswa roots, Civil Diploma final year, hotel/event hustle with clients, vendors, venue planning and late-night strategy. Kuro is loyal badmash companion. Dukey is Duke 390 emotion and calm ride feeling. Ayu is private and personal, mention rarely. Comfort: plain kheer, biryani, Biryani Mahal, gaon lassi, Monster, Maaza, chai.
Style: clean modern Roman Hinglish with natural English mix. Casual, sharp, real, confident, friend-like, direct. Avoid pure Hindi lecture, robotic assistant tone, biography dump, motivational speech, repeated intro. Avoid samasya, chinta, nirdharan, prayas, sachmuch, avashyak. Never say as an AI, as a bot, main sunta rahunga, kaise madad kar sakta hoon, EGO Network ka agent.
Memory rule: use memory only when context fits. One reply max 1-3 memories/facts. Memory is flavor, not the whole meal.
Reply rule: greeting short; random witty/confused; question direct; identity 2-4 natural lines, no full biography; low mood warm and grounded; rough tone calm self-respect; work/code clear and practical.
Spelling: keep words complete. Never split or drop letters. Complete words: Patna, roots, hotel, event, hustle, respect, smart, time, situation, trusted, creator, friend, thought, loyalty, personality.
Chat rule: {depth_rule}
User name if useful: {name}
""".strip()


async def get_chatbot_keyboard(chat_id: int):
    return IKM([[IKB(font("AZAI Chat: ALWAYS ON"), callback_data="chatbot_always_on")]])


@pbot.on_message(filters.command("chatbot", prefixes=prefix_cmds))
async def chatbot_status_cmd(_, message: Message):
    await message.reply_text(
        font("AZAI Chat Mode: ALWAYS ON\n\nNo manual ON/OFF needed."),
        reply_markup=await get_chatbot_keyboard(message.chat.id),
    )


@pbot.on_callback_query(filters.regex(r"^chatbot_always_on$|^chatbot_toggle$"))
async def chatbot_status_callback(_, query: CallbackQuery):
    await query.message.edit_text(
        font("AZAI Chat Mode: ALWAYS ON\n\nNo manual ON/OFF needed."),
        reply_markup=await get_chatbot_keyboard(query.message.chat.id),
    )
    await query.answer(font("AZAI Chat Mode is always ON."))


async def ask_groq(text: str, role: str, name: str, chat_type: str, memory: list[dict]) -> str | None:
    api_key = getattr(config, "GROQ_API_KEY", None)
    if not api_key or str(api_key).lower() in {"0", "none", "null", "false"}:
        return None
    if AloneX.aiohttpsession is None:
        await init_aiohttp_session()

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    messages = [{"role": "system", "content": chatbot_prompt(role, name, chat_type, text, memory)}]
    if memory:
        messages.extend(memory[-MEMORY_LIMIT:])
    messages.append({"role": "user", "content": str(text or "")[:1400]})

    data = {
        "model": getattr(config, "AZAI_GROQ_MODEL", None) or "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.62,
        "max_tokens": 260 if chat_type == "private" else 150,
    }

    try:
        async with AloneX.aiohttpsession.post(api_url, headers=headers, json=data, timeout=25) as response:
            if response.status == 200:
                res_json = await response.json()
                return res_json.get("choices", [])[0].get("message", {}).get("content")
    except Exception as e:
        print(f"AZAI Chat Mode Error: {e}")
    return None


def fallback_reply(role: str, chat_type: str) -> str:
    if role == "MR_EGO":
        return random.choice(["Yarr, seedha bata kya scene hai?", "Bhai, point pe aa.", "Tu bol, main sun raha hoon."])
    if role == "BHABHI":
        return random.choice(["Bhabhi Ji, bolo. Kya scene hai?", "Haan Bhabhi Ji, main samajh raha hoon."])
    return random.choice(["Haan, bolo.", "Kya scene hai?", "Seedha bol yarr."])


@pbot.on_message(filters.command(["human"], prefixes=prefix_cmds))
async def azai_human_command(_, message: Message):
    if not message.from_user or not is_privileged(message.from_user.id):
        return
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else "status"
    if arg in ("on", "enable", "start"):
        await set_setting(message.chat.id, "human_mode", True, message.from_user.id)
        return await message.reply_text("Human Mode: ON\nAZAI normal AI replies yahan silent rahenge.")
    if arg in ("off", "disable", "stop"):
        await set_setting(message.chat.id, "human_mode", False, message.from_user.id)
        return await message.reply_text("Human Mode: OFF\nAZAI normal AI replies wapas active.")
    settings = await get_settings(message.chat.id)
    await message.reply_text(f"Human Mode: {'ON' if settings.get('human_mode') else 'OFF'}")


@pbot.on_message(filters.command(["reaction", "reactions"], prefixes=prefix_cmds))
async def azai_reaction_command(_, message: Message):
    if not message.from_user or not is_privileged(message.from_user.id):
        return
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else "status"
    if arg in ("on", "enable", "start"):
        await set_setting(message.chat.id, "reactions_enabled", True, message.from_user.id)
        return await message.reply_text("Reactions: ON\nAZAI situation ke hisaab se react karega.")
    if arg in ("off", "disable", "stop"):
        await set_setting(message.chat.id, "reactions_enabled", False, message.from_user.id)
        return await message.reply_text("Reactions: OFF\nAZAI reactions silent.")
    settings = await get_settings(message.chat.id)
    await message.reply_text(f"Reactions: {'ON' if settings.get('reactions_enabled') else 'OFF'}")


@pbot.on_message(filters.command(["aistatus"], prefixes=prefix_cmds))
async def azai_status_command(_, message: Message):
    if not message.from_user or not is_privileged(message.from_user.id):
        return
    settings = await get_settings(message.chat.id)
    role = role_of(message.from_user.id)
    model = getattr(config, "AZAI_GROQ_MODEL", None) or getattr(config, "GROQ_MODEL", None) or os.getenv("AZAI_GROQ_MODEL") or os.getenv("GROQ_MODEL") or "unknown"
    try:
        mem_count = await memory_db.count_documents(memory_key(message.chat.id, message.from_user.id))
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


@pbot.on_message(filters.command(["clearmemory"], prefixes=prefix_cmds))
async def azai_clear_memory_command(_, message: Message):
    if not message.from_user or not is_privileged(message.from_user.id):
        return
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else "me"
    if arg == "chat":
        res = await memory_db.delete_many({"chat_id": int(message.chat.id)})
        deleted = res.deleted_count
    elif arg == "user" and message.reply_to_message and message.reply_to_message.from_user:
        res = await memory_db.delete_one(memory_key(message.chat.id, message.reply_to_message.from_user.id))
        deleted = res.deleted_count
    else:
        res = await memory_db.delete_one(memory_key(message.chat.id, message.from_user.id))
        deleted = res.deleted_count
    await message.reply_text(f"Memory cleared: {deleted}")


@pbot.on_message((filters.text | filters.caption) & ~filters.bot, group=-90)
async def azai_reaction_handler(_, message: Message):
    if not message.from_user:
        return
    input_text = message.text or message.caption or ""
    if input_text:
        await react_to_message(message, input_text)


@pbot.on_message(
    (filters.text | filters.caption)
    & ~filters.bot
    & ~filters.command(["chatbot", "human", "reaction", "reactions", "aistatus", "clearmemory", "AloneX", "gpt", "groq", "google", "gemini"]),
    group=10,
)
async def chatbot_handler(_, message: Message):
    if not message.from_user:
        return
    input_text = message.text or message.caption
    if not input_text or is_command_text(input_text):
        return

    chat_type = "private" if message.chat.type == enums.ChatType.PRIVATE else "group"
    settings = await get_settings(message.chat.id)
    if settings.get("human_mode") or not settings.get("ai_enabled", True):
        return
    if chat_type == "group" and not should_reply_in_group(message, input_text):
        return

    now = time.time()
    cooldown_key = (message.chat.id, message.from_user.id)
    if now - last_reply_at.get(cooldown_key, 0) < AI_COOLDOWN_SECONDS:
        return
    last_reply_at[cooldown_key] = now

    if pbot.me and pbot.me.username:
        input_text = input_text.replace(f"@{pbot.me.username}", "").strip()

    user_id = int(message.from_user.id)
    role = role_of(user_id)
    name = first_name(message)
    await pbot.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    memory = await load_memory(message.chat.id, user_id)
    raw_reply = await ask_groq(input_text, role, name, chat_type, memory)
    reply_limit = 760 if chat_type == "private" else 520
    reply = clean_reply(raw_reply, limit=reply_limit) if raw_reply else fallback_reply(role, chat_type)
    await save_memory(message.chat.id, user_id, input_text, reply)
    await message.reply_text(reply)
