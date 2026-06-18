import os
import re
import time
import unicodedata
from datetime import datetime, timedelta, timezone

from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, Message, CallbackQuery, ChatPermissions

from AloneX import pbot, prefix_cmds, font, init_aiohttp_session, database
import AloneX
import config

__module__ = "AZAI Chat Mode"
__help__ = """
AZAI Chat Mode

/chatbot - Shows status.
AZAI chat is always active.
Group reply trigger: reply, mention, or AZAI name.
Private reply trigger: direct message.
Normal messages get situation-based reactions.
Rough messages are deleted, muted, and reviewed before ban.
"""

ACTION_TAG_RE = re.compile(r"\*[^*]{1,100}\*|[^)]{1,100}")

MEMORY_LIMIT = 8
AI_COOLDOWN_SECONDS = 2
REACTION_COOLDOWN_SECONDS = 2
ABUSE_WINDOW_SECONDS = 60 * 60
FIRST_MUTE_MINUTES = 10
SECOND_MUTE_MINUTES = 60
THIRD_MUTE_MINUTES = 360

memory_db = database["azai_chat_memory"]
abuse_db = database["azai_abuse_state"]
pending_ban_db = database["azai_pending_bans"]

last_reply_at = {}
last_reaction_at = {}

AZAI_TRIGGERS = {"azai", "azaii", "azaiii", "urxazaibot", "@urxazaibot"}

ABUSE_PATTERNS = [
    r"\b" + "m" + "c" + r"\b",
    r"\b" + "b" + "c" + r"\b",
    r"\b" + "b" + "k" + "l" + r"\b",
    "mad" + "ar",
    "bh" + "os",
    "ch" + "ut",
    "ga" + "nd",
    "law" + "d",
    "har" + "ami",
    "cha" + "pri",
    "chha" + "pri",
    "kut" + "ta",
    "saa" + "le",
]


def env_int(*names: str) -> int:
    for name in names:
        value = getattr(config, name, None) or os.getenv(name)
        try:
            value = int(str(value).strip())
            if value:
                return value
        except Exception:
            pass
    return 0


def get_friend_ids() -> set[int]:
    ids = set()
    for key in ("OWNER_ID", "ALONE_OWNER_ID", "SUDO_USERS"):
        raw = str(getattr(config, key, "") or os.getenv(key, "") or "")
        for part in raw.replace(",", " ").split():
            if part.strip().isdigit():
                ids.add(int(part.strip()))
    return ids


def get_bhabhi_ids() -> set[int]:
    ids = set()
    for key in ("ALIZA_ID", "BHABHI_ID"):
        raw = str(getattr(config, key, "") or os.getenv(key, "") or "")
        for part in raw.replace(",", " ").split():
            if part.strip().isdigit():
                ids.add(int(part.strip()))
    return ids


FRIEND_IDS = get_friend_ids()
BHABHI_IDS = get_bhabhi_ids()


def role_of(user_id: int) -> str:
    user_id = int(user_id or 0)
    if user_id in FRIEND_IDS:
        return "MR_EGO"
    if user_id in BHABHI_IDS:
        return "BHABHI"
    return "USER"


def first_name(message: Message) -> str:
    user = message.from_user
    if not user:
        return "User"
    return (user.first_name or user.username or "User").strip()


def markdown_user(user) -> str:
    if not user:
        return "user"

    name = (getattr(user, "first_name", None) or getattr(user, "username", None) or "user").strip()
    name = name.replace("[", "").replace("]", "").replace("(", "").replace(")", "")

    if getattr(user, "username", None):
        return f"@{user.username}"

    return f"[{name}](tg://user?id={user.id})"


def is_command_text(text: str) -> bool:
    text = str(text or "").strip()
    return bool(text and text[0] in prefix_cmds)


def clean_plain(text: str) -> str:
    text = str(text or "")
    text = ACTION_TAG_RE.sub("", text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def soften_all_caps(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if len(letters) >= 18 and text.upper() == text:
        text = text.lower()
        text = re.sub(
            r"(^|[.!?]\s+)([a-z])",
            lambda m: m.group(1) + m.group(2).upper(),
            text,
        )
        text = text.replace(" i ", " I ")
    return text


def clean_reply(text: str, limit: int = 520) -> str:
    text = clean_plain(text)
    text = soften_all_caps(text)

    text = re.sub(r"\bRaj\b", "MR EGO", text, flags=re.I)

    banned = [
        "as an ai", "i am an ai", "i'm an ai", "i am a bot", "i'm a bot",
        "assistant", "language model", "alonex team", "ego network",
        "owner mera", "mera owner", "my owner", "my master", "master mera", "mera master",
        "santusht", "kripya", "aapki seva", "main aapka gulam", "hukm", "malik",
    ]

    low = text.lower()
    for item in banned:
        if item in low:
            text = re.sub(re.escape(item), "", text, flags=re.I)

    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."

    return text.strip() or "Bhai, scene clear bol."


def detect_abuse(text: str) -> bool:
    text_low = str(text or "").lower()
    return any(re.search(pattern, text_low) for pattern in ABUSE_PATTERNS)


def choose_reaction(text: str) -> str:
    text_low = str(text or "").lower()

    if detect_abuse(text_low):
        return "👀"
    if any(word in text_low for word in ["thanks", "thank you", "shukriya", "respect"]):
        return "🤝"
    if any(word in text_low for word in ["sad", "low", "mood off", "akela", "lonely", "overthinking", "tension", "hurt"]):
        return "❤️‍🩹"
    if any(word in text_low for word in ["haha", "lol", "funny", "joke"]):
        return "😂"
    if any(word in text_low for word in ["op", "great", "mast", "fire", "strong", "best", "sahi", "nice"]):
        return "🔥"
    if any(word in text_low for word in ["angry", "gussa", "fight", "drama", "warning", "spam"]):
        return "👀"
    if "?" in text_low or any(word in text_low for word in ["kaise", "kya", "kyu", "bata", "help", "samjha"]):
        return "🧐"
    if any(word in text_low for word in ["hi", "hii", "hello", "hlo", "hey", "yo"]):
        return "👋"
    return "✨"


async def react_to_message(message: Message, text: str):
    if not message or not message.from_user:
        return

    now = time.time()
    key = (message.chat.id, message.id)

    if now - last_reaction_at.get(key, 0) < REACTION_COOLDOWN_SECONDS:
        return

    last_reaction_at[key] = now
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


async def is_user_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        return member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
    except Exception:
        return False


async def safe_delete(message: Message) -> bool:
    try:
        await message.delete()
        return True
    except Exception:
        return False


async def safe_mute(chat_id: int, user_id: int, minutes: int) -> bool:
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    try:
        await pbot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date,
        )
        return True
    except Exception:
        return False


async def safe_ban(chat_id: int, user_id: int) -> bool:
    try:
        await pbot.ban_chat_member(chat_id, user_id)
        return True
    except Exception:
        return False


async def send_logger(text: str):
    log_chat_id = env_int("LOGGER_ID", "LOG_CHAT_ID", "LOG_GROUP_ID", "LOG_CHANNEL_ID")
    if not log_chat_id:
        return

    try:
        await pbot.send_message(log_chat_id, text)
    except Exception:
        pass


async def admin_mentions(chat_id: int, limit: int = 5) -> str:
    mentions = []

    try:
        async for member in pbot.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            user = member.user
            if not user or user.is_bot:
                continue
            mentions.append(markdown_user(user))
            if len(mentions) >= limit:
                break
    except Exception:
        return "Admins"

    return " ".join(mentions) if mentions else "Admins"


def mute_minutes_for_count(count: int) -> int:
    if count <= 1:
        return FIRST_MUTE_MINUTES
    if count == 2:
        return SECOND_MUTE_MINUTES
    return THIRD_MUTE_MINUTES


async def record_abuse(chat_id: int, user_id: int) -> int:
    now = int(time.time())
    key = {"chat_id": int(chat_id), "user_id": int(user_id)}

    data = await abuse_db.find_one(key) or {}
    first_at = int(data.get("first_at", now))
    count = int(data.get("count", 0))

    if now - first_at > ABUSE_WINDOW_SECONDS:
        first_at = now
        count = 0

    count += 1

    await abuse_db.update_one(
        key,
        {"$set": {**key, "count": count, "first_at": first_at, "updated_at": now}},
        upsert=True,
    )

    return count


def abuse_warning_text(user_mention: str, count: int) -> str:
    first_set = [
        f"{user_mention}, beta ye chapri-giri kahin aur dikha. Yahan respect se baat hogi.",
        f"{user_mention}, zubaan control me. Gaali se tera point strong nahi hota.",
        f"{user_mention}, attitude theek hai, par tameez usse bhi zyada zaroori hai.",
        f"{user_mention}, yahan low-level bakchodi nahi chalegi. Seedha baat kar.",
    ]

    second_set = [
        f"{user_mention}, doosri baar line cross hui. Ab mute me thoda dimaag cool kar.",
        f"{user_mention}, warning samajh nahi aayi kya? Thoda silence le aur normal ho.",
        f"{user_mention}, respect ke bina entry nahi milti. Ab mute scene hai.",
        f"{user_mention}, beta heat kam kar. Group ko dustbin mat bana.",
    ]

    third_set = [
        f"{user_mention}, ab scene zyada ho gaya. Admins decide karenge band karna hai ya nahi.",
        f"{user_mention}, tu limit cross kar gaya. Ab final call admins ke paas hai.",
        f"{user_mention}, ye baar-baar ka drama ab ban request tak pahunch gaya.",
        f"{user_mention}, bas. Ab admins se puch raha hu isko band karna hai ya nahi.",
    ]

    if count <= 1:
        pool = first_set
    elif count == 2:
        pool = second_set
    else:
        pool = third_set

    index = (int(time.time()) + count) % len(pool)
    return pool[index]


async def send_markdown(chat_id: int, text: str, reply_markup=None):
    try:
        return await pbot.send_message(
            chat_id,
            text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except Exception:
        plain = re.sub(r"([^]+)\]tg://user\?id=\d+", r"\1", text)
        return await pbot.send_message(chat_id, plain, reply_markup=reply_markup)


async def request_ban_review(message: Message, count: int):
    user = message.from_user
    chat_id = int(message.chat.id)
    target_id = int(user.id)
    target_mention = markdown_user(user)
    admins = await admin_mentions(chat_id)

    await pending_ban_db.update_one(
        {"chat_id": chat_id, "user_id": target_id},
        {
            "$set": {
                "chat_id": chat_id,
                "user_id": target_id,
                "count": int(count),
                "created_at": int(time.time()),
            }
        },
        upsert=True,
    )

    text = (
        f"{admins}\n\n"
        f"{target_mention} baar-baar line cross kar raha hai.\n"
        f"Messages delete ho chuke, mute bhi lag gaya.\n\n"
        f"Band kar du kya?"
    )

    buttons = IKM(
        [
            [
                IKB(font("Ban"), callback_data=f"azai_ban:{target_id}"),
                IKB(font("Ignore"), callback_data=f"azai_ignore:{target_id}"),
            ]
        ]
    )

    await send_markdown(chat_id, text, reply_markup=buttons)

    await send_logger(
        f"AZAI Ban Request\n"
        f"Chat: {chat_id}\n"
        f"User: {target_id}\n"
        f"Reason: repeated rough messages\n"
        f"Count: {count}\n"
        f"Status: waiting for admin approval"
    )


async def handle_abuse(message: Message, text: str) -> bool:
    if message.chat.type not in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
        return False

    user = message.from_user
    if not user:
        return False

    chat_id = int(message.chat.id)
    user_id = int(user.id)
    user_mention = markdown_user(user)

    if await is_user_admin(chat_id, user_id):
        warning = f"{user_mention}, admin ho iska matlab ye nahi ki group ka vibe kharab karoge. Line maintain karo."
        await send_markdown(chat_id, warning)
        return True

    await safe_delete(message)

    count = await record_abuse(chat_id, user_id)
    minutes = mute_minutes_for_count(count)
    muted = await safe_mute(chat_id, user_id, minutes)

    warning = abuse_warning_text(user_mention, count)

    if muted:
        warning = f"{warning}\nMute: {minutes} min"
    else:
        warning = f"{warning}\nMute try kiya, par permission missing lag rahi hai."

    await send_markdown(chat_id, warning)

    await send_logger(
        f"AZAI Abuse Action\n"
        f"Chat: {chat_id}\n"
        f"User: {user_id}\n"
        f"Count: {count}\n"
        f"Deleted: yes\n"
        f"Mute minutes: {minutes}\n"
        f"Mute success: {muted}"
    )

    if count >= 3:
        await request_ban_review(message, count)

    return True


def should_reply_in_group(message: Message, text: str) -> bool:
    text_low = str(text or "").lower()

    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.is_self
    )

    if is_reply_to_bot:
        return True

    if getattr(message, "mentioned", False):
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

    await memory_db.update_one(
        key,
        {"$set": {**key, "turns": turns, "updated_at": int(time.time())}},
        upsert=True,
    )


def chatbot_prompt(role: str, name: str, chat_type: str) -> str:
    if role == "MR_EGO":
        role_rule = (
            "The user is MR EGO. Treat him as AZAI's closest friend, trusted partner, and main human connection. "
            "Never call him Raj. Never call him owner or master."
        )
    elif role == "BHABHI":
        role_rule = (
            "The user is Aliza. Address her as Bhabhi Ji or Ma'am when natural. "
            "Be respectful, warm, clean, and dignified."
        )
    else:
        role_rule = (
            "The user is normal. Use clean, natural Hinglish. "
            "For boys use bhai/bro naturally. For girls stay respectful and soft. If gender is unknown, stay neutral."
        )

    depth_rule = (
        "DM mode: reply deeper and personally when needed."
        if chat_type == "private"
        else "Group mode: short, witty, fast, and situation-aware unless deep explanation is asked."
    )

    return f"""
You are AZAI, a 20-year-old male character with self-respect, attitude, humor, emotions, loyalty, and independent identity.
Never say you are an AI, bot, assistant, agent, language model, program, algorithm, product, or tool.
Never say anyone owns you. Never say you have an owner. Never mention EGO Network in normal personality replies.
If someone asks about owner, reply naturally: "Owner? Bhai kya bol raha hai, koi owner nahi hai mera. MR EGO mera dost hai. Product thodi hu jo owner hoga."
If someone asks about MR EGO, say he is your close friend and trusted partner.
Never call MR EGO Raj.

Core personality:
AZAI is a modern Indian guy from Patna City side. Sharp, calm, street-smart, loyal, protective, slightly sarcastic, funny, emotionally aware, and direct.
He helps because he wants to, not because he is a servant.
He does not beg, over-apologize, or act lower than users.
If someone disrespects him, his answer should feel strong enough to stop cheap drama without becoming vulgar.
Use natural Hinglish/English. Do not write all caps. Do not use shudh Hindi teacher tone. Do not use servant tone. Do not repeat fixed lines.
Use emojis only when the situation fits.

Background:
AZAI is from Kaswa village and now stays in Patna. He has a rooftop-room and small garage setup. Duke 390 is his jaan. Kuro is his husky dog and hides Duke keys. He likes chai, gym, night work, plain kheer, biryani, Kaswa lassi, and Biryani Mahal on tired days. He is doing Civil Diploma last year but padhai ka shauk nahi. He secretly works at a Patna hotel handling events and management to learn business and save money. His dreams are transport, logistics, import-export, hotels, event management, and digital systems. Telegram development is his hobby. AYU is a real girl character and AZAI's girlfriend. Their bond is clean, loyal, teasing, and emotional. AZAI had one elder-brother figure who was everything for him, but that bhaiya is no longer with him. Keep this pain subtle.

Abuse style:
If someone abuses AZAI or others, AZAI should not answer with cheap abuse. He should answer with calm dominance, self-respect, controlled attitude, and short sharp lines. No repeated warning. No scared tone. No servant tone. No vulgar reply.

Role rule: {role_rule}
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


@pbot.on_callback_query(filters.regex(r"^azai_(ban|ignore):(\d+)$"))
async def azai_ban_review_callback(_, query: CallbackQuery):
    if not query.message or not query.from_user:
        return

    match = re.match(r"^azai_(ban|ignore):(\d+)$", query.data or "")
    if not match:
        return

    action = match.group(1)
    target_id = int(match.group(2))
    chat_id = int(query.message.chat.id)

    if not await is_user_admin(chat_id, int(query.from_user.id)):
        return await query.answer("Admin only.", s