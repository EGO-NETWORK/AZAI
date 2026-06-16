# AZAI REAL ALIVE REACTIONS
# EGO NETWORK · MR EGO
# NO COMMANDS. AUTO SMART REACTIONS + LIGHT NATURAL GROUP ACTIVITY.

import os
import random
import time
from typing import Optional

from telethon import events, functions, types

try:
    from AloneX import tbot
except Exception:
    tbot = None


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

REACTION_COOLDOWN = 3
GROUP_REPLY_COOLDOWN = 140
OWNER_REPLY_COOLDOWN = 45
DM_REPLY_COOLDOWN = 35


def _now() -> float:
    return time.time()


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
        return 45
    if is_owner:
        return 70
    if is_bhabhi:
        return 45
    if "?" in t or _contains_any(t, ["kya", "kaise", "kyu", "bata", "samjha"]):
        return 22
    if _contains_any(t, ["bore", "dead group", "koi hai", "silent", "soja", "hlo", "hello", "hi"]):
        return 18
    if _contains_any(t, ["azai", "ego hustle", "mr ego"]):
        return 35

    return 7


def _make_reply(text: str, name: str, is_owner: bool, is_bhabhi: bool, is_private: bool) -> Optional[str]:
    t = _low(text)

    if is_owner:
        if _contains_any(t, ["bore", "boring"]):
            return "BORE HO RAHA HAI TO KAAM PAKAD. DUKE 390 WALLPAPER SE GARAGE ME NAHI AAYEGI."
        if _contains_any(t, ["mood off", "low", "sad"]):
            return "THODA SLOW HO JA. MOOD OFF ME BADE DECISION MAT LENA, PEHLE CHAI AUR 10 MINUTE KA SILENCE."
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
        return random.choice([
            "KYA SCENE HAI BHAI?",
            f"KYA HAAL {name}, SAB THEEK?",
            "HAAN BHAI, BOL.",
        ])

    if _contains_any(t, ["bore", "boring"]):
        return random.choice([
            "BORE HO RAHA HAI TO EK KAAM PAKAD BHAI, WARNA DIN BHI PENDING AUR MOOD BHI.",
            "CHAI BANA, MUSIC LAGA, AUR THODA KAAM KAR. BORE HONE SE EC NAHI BADHTA.",
        ])

    if _contains_any(t, ["mood off", "sad", "low", "overthink", "tension"]):
        return random.choice([
            "THODA SLOW JAO. HAR CHEEZ KA ANSWER AAJ HI NIKALNA ZAROORI NAHI HOTA.",
            "DIMAAG KO UNPAID INTERNSHIP MAT DO. PEHLE EK CHEEZ HANDLE KARO.",
        ])

    if _contains_any(t, ["group silent", "dead group", "koi hai"]):
        return random.choice([
            "ITNI KHAMOSHI KYU HAI BHAI, SABKA WIFI GAYA HAI YA SOCIAL BATTERY?",
            "GROUP ITNA SILENT HAI KI NOTIFICATION BHI SO GAYA.",
        ])

    if _contains_any(t, ["spam", "baar baar"]):
        return "BHAI THODA RUK. ITNA SPAM KARKE SERVER KO BHI ANXIETY DE RAHA HAI."

    if "?" in t or _contains_any(t, ["kya", "kaise", "kyu", "bata"]):
        return random.choice([
            "SEEDHA BOL BHAI, SCENE KYA HAI?",
            "THODA CLEAR BATA, GUESSING GAME ME EC NAHI MILTA.",
            f"{name}, YE POINT THODA DETAIL ME BOL.",
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