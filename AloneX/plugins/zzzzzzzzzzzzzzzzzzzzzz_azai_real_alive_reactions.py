# AZAI REAL ALIVE REACTIONS
# EGO NETWORK · MR EGO
# NO COMMANDS. AUTO SMART REACTIONS + IST TIME-AWARE GROUP ACTIVITY.

import os
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from telethon import events, functions, types

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

try:
    from AloneX import tbot
except Exception:
    tbot = None


IST = ZoneInfo("Asia/Kolkata") if ZoneInfo else timezone(timedelta(hours=5, minutes=30))
BOT_ID = None

OWNER_IDS = set()
for _key in ("OWNER_ID", "ALONE_OWNER_ID", "SUDO_USERS"):
    _val = os.getenv(_key, "")
    for _part in str(_val).replace(",", " ").split():
        if _part.strip().isdigit():
            OWNER_IDS.add(int(_part.strip()))

BHABHI_IDS = set()
for _key in ("ALIZA_ID", "BHABHI_ID"):
    _val = os.getenv(_key, "")
    for _part in str(_val).replace(",", " ").split():
        if _part.strip().isdigit():
            BHABHI_IDS.add(int(_part.strip()))


LAST_REACTION = {}
LAST_REPLY = {}

REACTION_COOLDOWN = 0
GROUP_REPLY_COOLDOWN = 45
OWNER_REPLY_COOLDOWN = 20
DM_REPLY_COOLDOWN = 15

DEEP_WORDS = ["mood off", "low", "overthink", "tension", "akela", "udaas", "silent", "khamosh"]
QUESTION_WORDS = ["kya", "kaise", "kyu", "why", "how", "?", "confuse", "samjha", "bata"]
ROUGH_WORDS = ["gali", "rough", "bad", "bakwas", "faltu", "spam", "chapri"]


def _now() -> float:
    return time.time()


def _ist_now() -> datetime:
    return datetime.now(IST)


def _time_mood() -> str:
    hour = _ist_now().hour
    if 4 <= hour < 7:
        return "EARLY"
    if 7 <= hour < 11:
        return "MORNING"
    if 11 <= hour < 17:
        return "DAY"
    if 17 <= hour < 20:
        return "EVENING"
    if 20 <= hour < 23:
        return "NIGHT"
    return "LATE_NIGHT"


def _festival_name() -> str:
    fixed = {
        "01-01": "NEW YEAR",
        "01-26": "REPUBLIC DAY",
        "08-15": "INDEPENDENCE DAY",
        "10-02": "GANDHI JAYANTI",
        "12-25": "CHRISTMAS",
    }
    env_festival = os.getenv("AZAI_TODAY_FESTIVAL", "").strip().upper()
    if env_festival:
        return env_festival
    return fixed.get(_ist_now().strftime("%m-%d"), "")


def _text(event) -> str:
    return (getattr(event, "raw_text", None) or "").strip()


def _low(text: str) -> str:
    return text.lower().strip()


def _first_name(sender) -> str:
    name = getattr(sender, "first_name", None) or getattr(sender, "username", None) or ""
    name = str(name).strip()
    if not name:
        return "BHAI"
    return name.split()[0][:18].upper()


def _is_command(text: str) -> bool:
    return text.strip().startswith(("/", "!", "."))


def _contains_any(text: str, words) -> bool:
    t = _low(text)
    return any(w in t for w in words)


def _should_skip(event, sender, text: str) -> bool:
    if not tbot:
        return True
    if not text:
        return True
    if _is_command(text):
        return True
    if getattr(sender, "bot", False):
        return True
    if getattr(event, "out", False):
        return True
    return False


def _pick_reaction(text: str, is_owner: bool, is_bhabhi: bool) -> str:
    t = _low(text)
    festival = _festival_name()
    if _contains_any(t, DEEP_WORDS):
        return random.choice(["❤️", "😔", "🤝"])
    if _contains_any(t, ROUGH_WORDS):
        return random.choice(["😐", "👀", "🤨"])
    if festival and _contains_any(t, ["happy", "festival", "wish", "diwali", "eid", "holi", "christmas"]):
        return random.choice(["✨", "❤️", "🔥"])
    if is_owner:
        return random.choice(["👑", "🔥", "🤝"])
    if is_bhabhi:
        return random.choice(["🤝", "❤️", "✨"])
    if _contains_any(t, ["haha", "hahaha", "lol", "😂", "🤣", "funny", "maja", "masti"]):
        return random.choice(["😂", "🤣"])
    if _contains_any(t, ["nice", "mast", "op", "best", "sahi", "good", "great", "fire", "strong"]):
        return random.choice(["🔥", "😎", "✨"])
    if _contains_any(t, QUESTION_WORDS):
        return random.choice(["🤔", "👀"])
    if _contains_any(t, ["raid", "heist", "work", "luck", "protect", "balance", "leaderboard", "rank", "ec"]):
        return random.choice(["⚡", "🔥", "💰"])
    if _time_mood() in ("NIGHT", "LATE_NIGHT"):
        return random.choice(["👀", "❤️", "😎"])
    return random.choice(["👀", "👍", "😎"])


async def _react(event, emoji: str) -> None:
    try:
        await tbot(functions.messages.SendReactionRequest(peer=await event.get_input_chat(), msg_id=event.id, reaction=[types.ReactionEmoji(emoticon=emoji)]))
    except Exception:
        return


async def _is_reply_to_me(event) -> bool:
    global BOT_ID
    try:
        if not event.is_reply:
            return False
        if BOT_ID is None:
            me = await tbot.get_me()
            BOT_ID = getattr(me, "id", None)
        reply = await event.get_reply_message()
        return bool(reply and BOT_ID and reply.sender_id == BOT_ID)
    except Exception:
        return False


async def _is_mention_to_me(text: str) -> bool:
    try:
        username = os.getenv("BOT_USERNAME", "Urxazaibot").replace("@", "").lower()
        return f"@{username}" in _low(text)
    except Exception:
        return False


def _reply_chance(event, text: str, is_owner: bool, is_bhabhi: bool, direct_to_me: bool) -> int:
    t = _low(text)
    if direct_to_me:
        return 100
    if _contains_any(t, DEEP_WORDS):
        return 100
    if _contains_any(t, ROUGH_WORDS):
        return 100
    if event.is_private:
        return 60
    if is_owner:
        return 85
    if is_bhabhi:
        return 65
    if _contains_any(t, QUESTION_WORDS):
        return 45
    if _contains_any(t, ["bore", "dead group", "koi hai", "silent", "soja", "hlo", "hello", "hi"]):
        return 30
    if _contains_any(t, ["azai", "ego hustle", "mr ego"]):
        return 50
    if _time_mood() in ("EVENING", "NIGHT", "LATE_NIGHT"):
        return 15
    return 10


def _festival_reply() -> Optional[str]:
    festival = _festival_name()
    if not festival:
        return None
    return random.choice([f"HAPPY {festival}. POSITIVE VIBE RAKH, SPAM NAHI.", f"{festival} KA SCENE HAI. GROUP LIGHT RAKHO."])


def _time_based_bore_reply() -> str:
    mood = _time_mood()
    if mood == "EARLY":
        return "SUBAH-SUBAH BORE? PEHLE CHAI, PHIR EK CHHOTA KAAM."
    if mood == "MORNING":
        return "MORNING HAI BHAI, KAAM PAKAD. DIN WASTE MAT KAR."
    if mood == "DAY":
        return "DAY WORK MODE HAI. BORE HONE SE EC NAHI BADHEGA."
    if mood == "EVENING":
        return "EVENING HAI. MUSIC LAGA AUR GROUP KO ZINDA KAR."
    if mood == "NIGHT":
        return "RAAT ME BORE HAI TO MUSIC LAGA. DIMAAG KO EXTRA LOAD MAT DE."
    return "LATE NIGHT HAI. SLOW HO JA, KAL BHI DIN HAI."


def _time_based_mood_reply() -> str:
    mood = _time_mood()
    if mood in ("NIGHT", "LATE_NIGHT"):
        return "MOOD OFF HAI TO SLOW HO. HAR ANSWER AAJ HI NIKALNA ZAROORI NAHI."
    if mood == "DAY":
        return "MOOD OFF HAI TO EK SMALL TASK KAR. MOMENTUM WAPAS AATA HAI."
    return "THODA PAUSE LE. KAAM EK-EK STEP ME HOGA."


def _make_reply(text: str, name: str, is_owner: bool, is_bhabhi: bool, is_private: bool) -> Optional[str]:
    t = _low(text)
    if _contains_any(t, ROUGH_WORDS):
        return "GAALI SAMAJH AATI HAI. AB KAAM BATA, MAIN SOLVE KAR DUNGA."
    if _contains_any(t, ["diwali", "eid", "holi", "christmas", "festival", "happy"]):
        festival_line = _festival_reply()
        if festival_line:
            return festival_line
    if _contains_any(t, ["bore", "boring"]):
        return _time_based_bore_reply()
    if _contains_any(t, DEEP_WORDS):
        if is_bhabhi:
            return "BHABHI JI, THODA SLOW HO JAIYE. SAB EK SAATH SOCHNA ZAROORI NAHI."
        if is_owner:
            return "SIR, MOOD OFF HAI TO PEHLE SLOW HO. BADE DECISION BAAD ME."
        return _time_based_mood_reply()
    if is_owner:
        if _contains_any(t, ["kar", "fix", "repo", "azai"]):
            return "MR EGO, SCENE SIMPLE HAI. PEHLE STABLE, PHIR STYLISH."
        return random.choice(["SCENE BATA SIR.", "KAAM BATA, DIRECT DEKHTA HU.", "IDEA STRONG HAI TO EXECUTION CLEAN RAKH."])
    if is_bhabhi:
        return random.choice(["BHABHI JI, SCENE CLEAR BATAIYE.", "MAAM, POINT BATAIYE. MAIN DEKH LETA HU."])
    if _contains_any(t, ["hi", "hello", "hlo", "hey", "azai"]):
        return random.choice(["BOL BHAI, SCENE KYA HAI?", "HAAN BHAI, KAAM BATA.", "BOL, KYA CHAL RAHA?"])
    if _contains_any(t, ["group silent", "dead group", "koi hai"]):
        return random.choice(["GROUP ITNA SILENT KYU HAI, SAB BACKGROUND APP BAN GAYE?", "KOI ACTIVE HAI YA SAB OFFLINE ACTING KAR RAHE?"])
    if _contains_any(t, ["spam", "baar baar"]):
        return "BHAI THODA RUK. ITNA SPAM SERVER KO BHI THAKA DEGA."
    if _contains_any(t, QUESTION_WORDS):
        return random.choice(["SEEDHA BOL BHAI, SCENE KYA HAI?", "THODA CLEAR BATA, GUESSING GAME NAHI.", f"{name}, POINT DETAIL ME BOL."])
    if _time_mood() == "LATE_NIGHT":
        return random.choice(["LATE NIGHT SCENE LAG RAHA HAI.", "AAGE BOL, ABHI SUN RAHA HU."])
    return random.choice(["HMM, SCENE SAMAJH GAYA.", "SAHI HAI BHAI.", "AAGE BOL."])


async def _maybe_reply(event, text: str, sender, is_owner: bool, is_bhabhi: bool, direct_to_me: bool) -> None:
    try:
        now = _now()
        cooldown = OWNER_REPLY_COOLDOWN if is_owner else (DM_REPLY_COOLDOWN if event.is_private else GROUP_REPLY_COOLDOWN)
        last = LAST_REPLY.get(event.chat_id, 0)
        if now - last < cooldown and not direct_to_me and not _contains_any(text, DEEP_WORDS + ROUGH_WORDS):
            return
        chance = _reply_chance(event, text, is_owner, is_bhabhi, direct_to_me)
        if random.randint(1, 100) > chance:
            return
        name = _first_name(sender)
        reply = _make_reply(text, name, is_owner, is_bhabhi, event.is_private)
        if not reply:
            return
        LAST_REPLY[event.chat_id] = now
        await event.reply(reply)
    except Exception:
        return


if tbot:
    @tbot.on(events.NewMessage(incoming=True))
    async def azai_real_alive_reactions(event):
        try:
            sender = await event.get_sender()
            text = _text(event)
            if _should_skip(event, sender, text):
                return
            user_id = int(getattr(sender, "id", 0) or 0)
            is_owner = user_id in OWNER_IDS
            is_bhabhi = user_id in BHABHI_IDS
            direct_to_me = False
            if await _is_reply_to_me(event):
                direct_to_me = True
            if await _is_mention_to_me(text):
                direct_to_me = True
            emoji = _pick_reaction(text, is_owner, is_bhabhi)
            await _react(event, emoji)
            await _maybe_reply(event, text, sender, is_owner, is_bhabhi, direct_to_me)
        except Exception:
            return
