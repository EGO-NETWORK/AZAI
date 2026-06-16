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

REACTION_COOLDOWN = 2
GROUP_REPLY_COOLDOWN = 120
OWNER_REPLY_COOLDOWN = 40
DM_REPLY_COOLDOWN = 30


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

    if festival and _contains_any(t, ["happy", "festival", "wish", "diwali", "eid", "holi", "christmas"]):
        return random.choice(["✨", "❤️", "🔥"])

    if is_owner:
        if _contains_any(t, ["done", "kar", "fix", "repo", "azai", "ego", "hustle"]):
            return random.choice(["🔥", "⚡", "🤝"])
        return random.choice(["👑", "🔥", "😎", "🤝"])

    if is_bhabhi:
        return random.choice(["🤝", "❤️", "✨"])

    if _contains_any(t, ["haha", "hahaha", "lol", "😂", "🤣", "funny", "maja", "masti"]):
        return random.choice(["😂", "🤣"])

    if _contains_any(t, ["sad", "mood off", "low", "alone", "lonely", "overthink", "tension", "cry"]):
        return random.choice(["❤️", "😔"])

    if _contains_any(t, ["nice", "mast", "op", "best", "sahi", "good", "great", "fire"]):
        return random.choice(["🔥", "😎", "✨"])

    if _contains_any(t, ["kya", "kaise", "kyu", "why", "how", "?", "confuse", "samjha"]):
        return random.choice(["🤔", "👀"])

    if _contains_any(t, ["raid", "heist", "work", "luck", "protect", "balance", "leaderboard", "rank", "ec"]):
        return random.choice(["⚡", "🔥", "💰"])

    if _contains_any(t, ["spam", "bakchodi", "faltu", "chapri"]):
        return random.choice(["😐", "👀"])

    mood = _time_mood()
    if mood in ("NIGHT", "LATE_NIGHT"):
        return random.choice(["👀", "❤️", "😎"])

    return random.choice(["👀", "👍", "😎"])


async def _react(event, emoji: str) -> None:
    try:
        now = _now()
        last = LAST_REACTION.get(event.chat_id, 0)
        if now - last < REACTION_COOLDOWN:
            return

        LAST_REACTION[event.chat_id] = now

        await tbot(
            functions.messages.SendReactionRequest(
                peer=await event.get_input_chat(),
                msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=emoji)],
            )
        )
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
        username = os.getenv("BOT_USERNAME", "Urxazaibot")
        username = username.replace("@", "").lower()
        return f"@{username}" in _low(text)
    except Exception:
        return False


def _reply_chance(event, text: str, is_owner: bool, is_bhabhi: bool, direct_to_me: bool) -> int:
    t = _low(text)

    if direct_to_me:
        return 100
    if event.is_private:
        return 50
    if is_owner:
        return 75
    if is_bhabhi:
        return 50
    if "?" in t or _contains_any(t, ["kya", "kaise", "kyu", "bata", "samjha"]):
        return 25
    if _contains_any(t, ["bore", "dead group", "koi hai", "silent", "soja", "hlo", "hello", "hi"]):
        return 20
    if _contains_any(t, ["azai", "ego hustle", "mr ego"]):
        return 38

    mood = _time_mood()
    if mood in ("EVENING", "NIGHT"):
        return 10
    if mood == "LATE_NIGHT":
        return 13

    return 7


def _festival_reply() -> Optional[str]:
    festival = _festival_name()
    if not festival:
        return None

    return random.choice([
        f"HAPPY {festival}. SCENE SOFT RAKH, AAJ KA DIN DRAMA KE LIYE NAHI HAI.",
        f"{festival} KA VIBE HAI. GROUP ME THODA LIGHT RAKHO, SPAM MAT KARNA.",
        f"AAJ {festival} HAI, TOH THODA POSITIVE REHNA BANTA HAI.",
    ])


def _time_based_bore_reply() -> str:
    mood = _time_mood()

    if mood == "EARLY":
        return "SUBAH-SUBAH BORE? BHAI DIN ABHI START HUA HAI, PEHLE CHAI AUR EK CHHOTA KAAM."
    if mood == "MORNING":
        return "MORNING ME BORE HO RAHA HAI TO KAAM PAKAD. DIN KO ABHI SE WASTE MAT KAR."
    if mood == "DAY":
        return "DAY WORK MODE HAI BHAI. BORE HONE SE EC NAHI BADHEGA, WORK KAR."
    if mood == "EVENING":
        return "EVENING HAI, MUSIC LAGA AUR GROUP KO THODA ZINDA KAR. SCENE SIMPLE HAI."
    if mood == "NIGHT":
        return "RAAT ME BORE HONA DANGEROUS HAI, DIMAAG EXTRA SOCHNA START KAR DETA HAI. MUSIC LAGA."
    return "LATE NIGHT HAI. DIMAAG KO OVERTHINKING KA CONTRACT MAT DE, THODA SLOW HO JA."


def _time_based_mood_reply() -> str:
    mood = _time_mood()

    if mood in ("NIGHT", "LATE_NIGHT"):
        return "RAAT ME MOOD OFF HO TOH THODA SLOW REH. HAR ANSWER AAJ HI NIKALNA ZAROORI NAHI."
    if mood == "DAY":
        return "MOOD OFF HAI TOH EK SMALL TASK KAR. KABHI-KABHI MOTIVATION KAAM KE BAAD AATI HAI."
    return "THODA PAUSE LE. DIMAAG KO UNPAID INTERNSHIP MAT DO."


def _make_reply(text: str, name: str, is_owner: bool, is_bhabhi: bool, is_private: bool) -> Optional[str]:
    t = _low(text)

    if _contains_any(t, ["diwali", "eid", "holi", "christmas", "festival", "happy"]):
        festival_line = _festival_reply()
        if festival_line:
            return festival_line

    if is_owner:
        if _contains_any(t, ["bore", "boring"]):
            return _time_based_bore_reply()
        if _contains_any(t, ["mood off", "low", "sad", "overthink"]):
            return _time_based_mood_reply()
        if _contains_any(t, ["kar", "fix", "repo", "azai"]):
            return "MR EGO, SCENE SIMPLE HAI. PEHLE STABLE, PHIR STYLISH. FALTU DRAMA NAHI."
        return random.choice([
            "SCENE SIMPLE HAI. KAAM BATAO.",
            "MR EGO AA GAYE, AB GROUP THODA SEEDHA BEHAVE KARE.",
            "IDEA STRONG HAI. BAS EXECUTION ME BAKCHODI NAHI CHAHIYE.",
        ])

    if is_bhabhi:
        return random.choice([
            "BHABHI JI, AAP TENSION MAT LIJIYE. SCENE HANDLE HO JAYEGA.",
            "MA'AM, AAPKA POINT SAHI HAI. MAIN CALMLY DEKH RAHA HOON.",
        ])

    if _contains_any(t, ["hi", "hello", "hlo", "hey"]):
        mood = _time_mood()
        if mood in ("NIGHT", "LATE_NIGHT"):
            return random.choice([
                "HAAN BHAI, RAAT KA SCENE KYA HAI?",
                f"KYA HAAL {name}, RAAT ME ABHI TAK ACTIVE?",
                "BOL BHAI, LATE NIGHT ME KYA CHAL RAHA HAI?",
            ])
        return random.choice([
            "KYA SCENE HAI BHAI?",
            f"KYA HAAL {name}, SAB THEEK?",
            "HAAN BHAI, BOL.",
        ])

    if _contains_any(t, ["bore", "boring"]):
        return _time_based_bore_reply()

    if _contains_any(t, ["mood off", "sad", "low", "overthink", "tension"]):
        return _time_based_mood_reply()

    if _contains_any(t, ["group silent", "dead group", "koi hai"]):
        return random.choice([
            "ITNI KHAMOSHI KYU HAI BHAI, SABKA WIFI GAYA HAI YA SOCIAL BATTERY?",
            "GROUP ITNA SILENT HAI KI NOTIFICATION BHI SO GAYA.",
            "KOI ZINDA HAI YA SAB BACKGROUND APP BAN GAYE?",
        ])

    if _contains_any(t, ["spam", "baar baar"]):
        return "BHAI THODA RUK. ITNA SPAM KARKE SERVER KO BHI ANXIETY DE RAHA HAI."

    if "?" in t or _contains_any(t, ["kya", "kaise", "kyu", "bata"]):
        return random.choice([
            "SEEDHA BOL BHAI, SCENE KYA HAI?",
            "THODA CLEAR BATA, GUESSING GAME ME EC NAHI MILTA.",
            f"{name}, YE POINT THODA DETAIL ME BOL.",
        ])

    mood = _time_mood()
    if mood == "LATE_NIGHT":
        return random.choice([
            "HMM, LATE NIGHT WALA SCENE LAG RAHA HAI.",
            "RAAT ME BAATEIN THODI REAL HO JATI HAIN.",
            "AAGE BOL, ABHI SUN RAHA HOON.",
        ])

    return random.choice([
        "HMM, SCENE SAMAJH RAHA HOON.",
        "SAHI HAI BHAI.",
        "AAGE BOL.",
        "YE THODA INTERESTING HAI.",
    ])


async def _maybe_reply(event, text: str, sender, is_owner: bool, is_bhabhi: bool, direct_to_me: bool) -> None:
    try:
        now = _now()
        cooldown = OWNER_REPLY_COOLDOWN if is_owner else (DM_REPLY_COOLDOWN if event.is_private else GROUP_REPLY_COOLDOWN)
        last = LAST_REPLY.get(event.chat_id, 0)

        if now - last < cooldown and not direct_to_me:
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