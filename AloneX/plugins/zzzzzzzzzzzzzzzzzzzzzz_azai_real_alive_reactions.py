# AZAI Real Alive Reactions
# EGO Network · MR EGO
# No commands. Auto smart reactions + light natural group activity.

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
        return "bhai"
    return name.split()[0][:18]


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

    if _contains_any(t, ["haha", "hahaha", "lol", "lmao", "😂", "🤣", "funny", "maja", "masti"]):
        return random.choice(["😂", "🤣"])

    if _contains_any(t, ["sad", "mood off", "low", "alone", "lonely", "overthink", "tension", "depressed", "cry"]):
        return random.choice(["❤️", "🫂", "😔"])

    if _contains_any(t, ["nice", "mast", "op", "best", "sahi", "good", "great", "awesome", "fire"]):
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
        key = (event.chat_id, event.id)
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
        if not username:
            return False
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
            return "Boss, bore ho raha hai to kaam pakad. Duke 390 wallpaper se garage me nahi aayegi."
        if _contains_any(t, ["mood off", "low", "sad"]):
            return "Boss, thoda slow ho ja. Mood off me bade decision mat lena, pehle chai aur 10 minute ka silence."
        if _contains_any(t, ["kar", "fix", "repo", "azai"]):
            return "MR EGO, scene simple hai. Pehle stable, phir stylish. Faltu drama nahi."
        return random.choice([
            "Boss, scene simple hai. Kaam batao.",
            "MR EGO aa gaye, ab group thoda seedha behave kare.",
            "Boss, idea strong hai. Bas execution me bakchodi nahi chahiye.",
        ])

    if is_bhabhi:
        return random.choice([
            "Bhabhi Ji, aap tension mat lijiye. Scene handle ho jayega.",
            "Ma’am, aapka point sahi hai. Main calmly dekh raha hoon.",
        ])

    if _contains_any(t, ["hi", "hello", "hlo", "hey"]):
        return random.choice([
            "Kya scene hai bhai?",
            f"Kya haal {name}, sab theek?",
            "Haan bhai, bol.",
        ])

    if _contains_any(t, ["bore", "boring"]):
        return random.choice([
            "Bore ho raha hai to ek kaam pakad bhai, warna din bhi pending aur mood bhi.",
            "Chai bana, music laga, aur thoda kaam kar. Bore hone se EC nahi badhta.",
        ])

    if _contains_any(t, ["mood off", "sad", "low", "overthink", "tension"]):
        return random.choice([
            "Thoda slow jao. Har cheez ka answer aaj hi nikalna zaroori nahi hota.",
            "Dimaag ko unpaid internship mat do. Pehle ek cheez handle karo.",
        ])

    if _contains_any(t, ["group silent", "dead group", "koi hai"]):
        return random.choice([
            "Itni khamoshi kyun hai bhai, sabka WiFi gaya hai ya social battery?",
            "Group itna silent hai ki notification bhi so gaya.",
        ])

    if _contains_any(t, ["spam", "baar baar"]):
        return "Bhai thoda ruk. Itna spam karke server ko bhi anxiety de raha hai."

    if "?" in t or _contains_any(t, ["kya", "kaise", "kyu", "bata"]):
        return random.choice([
            "Seedha bol bhai, scene kya hai?",
            "Thoda clear bata, guessing game me EC nahi milta.",
            f"{name}, ye point thoda detail me bol.",
        ])

    return random.choice([
        "Hmm, scene samajh raha hoon.",
        "Sahi hai bhai.",
        "Aage bol.",
        "Ye thoda interesting hai.",
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