import os
import random
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
abuse_db = database["azai_abuse_guard"]
pending_db = database["azai_pending_ban_reviews"]

ABUSE_WINDOW_SECONDS = 24 * 60 * 60
FLOOD_WINDOW_SECONDS = 8
FLOOD_LIMIT = 6
STICKER_WINDOW_SECONDS = 20
STICKER_LIMIT = 5
MUTE_MINUTES = 10
REVIEW_STRIKES = 3

msg_cache = defaultdict(lambda: deque(maxlen=20))
sticker_cache = defaultdict(lambda: deque(maxlen=20))

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
    "kut" + "ta",
    "saa" + "le",
]
ABUSE_RE = re.compile("|".join(ABUSE_PATTERNS), re.IGNORECASE)

USER_WARNINGS = [
    "{user} yahan low-level bakchodi nahi chalegi. Seedha baat kar.",
    "{user} tone control. Group clean rahega, drama nahi.",
    "{user} words sambhal. Respect se baat kar, warna system handle karega.",
    "{user} yeh group kachra zone nahi hai. Line me aa.",
    "{user} faltu heat nahi. Seedha point bol, personal mat ja.",
]

ADMIN_WARNINGS = [
    "{user}, admin side se thoda standard maintain karo. Group tumhe dekh ke line pakadta hai.",
    "{user}, admin ho. Example set karo, scene mat bigado.",
    "{user}, friendly reminder: authority ke saath tone bhi clean rakho.",
    "{user}, group ka control tabhi premium lagta hai jab admins bhi clean bolte hain.",
]


def now_ist() -> str:
    return datetime.now(IST).strftime("%d %b %Y - %I:%M %p")


async def send_log(text: str):
    targets = []
    for key in ("LOGGER_ID", "LOG_GROUP_ID", "LOG_CHAT_ID", "LOG_CHANNEL_ID"):
        value = os.getenv(key)
        if value and str(value).lstrip("-").isdigit():
            targets.append(int(value))
    for target in set(targets):
        try:
            await tbot.send_message(target, text)
        except Exception:
            pass


async def is_admin(event) -> bool:
    try:
        sender = await event.get_sender()
        if not sender or getattr(sender, "bot", False):
            return True
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


def mention_user(user, user_id: int) -> str:
    username = getattr(user, "username", None)
    if username:
        return f"@{username}"
    name = getattr(user, "first_name", None) or "User"
    return f"{name} ({user_id})"


async def safe_delete(event):
    try:
        await event.delete()
    except Exception:
        pass


async def mute_user(event, minutes: int):
    try:
        until = datetime.utcnow() + timedelta(minutes=minutes)
        await event.client.edit_permissions(event.chat_id, event.sender_id, until_date=until, send_messages=False)
        return True
    except Exception:
        return False


async def add_strike(chat_id: int, user_id: int, reason: str) -> int:
    key = {"chat_id": int(chat_id), "user_id": int(user_id)}
    old = await abuse_db.find_one(key) or {}
    first_at = int(old.get("first_at", 0) or 0)
    now = int(time.time())
    count = int(old.get("count", 0) or 0)
    if not first_at or now - first_at > ABUSE_WINDOW_SECONDS:
        count = 0
        first_at = now
    count += 1
    await abuse_db.update_one(
        key,
        {"$set": {**key, "count": count, "first_at": first_at, "last_reason": reason, "updated_at": now_ist()}},
        upsert=True,
    )
    return count


def review_buttons(chat_id: int, user_id: int):
    return [[
        Button.inline(font("Ban"), f"azab_ban|{chat_id}|{user_id}".encode()),
        Button.inline(font("Ignore"), f"azab_ignore|{chat_id}|{user_id}".encode()),
    ]]


def user_warning_text(name: str, count: int, muted: bool) -> str:
    line = random.choice(USER_WARNINGS).format(user=name)
    action = f"Mute: {MUTE_MINUTES} min" if muted else "Mute failed: check AZAI admin permission"
    return (
        font("AZAI MODERATION") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font(line) + "\n"
        + font("Strike:") + f" {count}/{REVIEW_STRIKES}\n"
        + font(action)
    )


def admin_warning_text(name: str) -> str:
    line = random.choice(ADMIN_WARNINGS).format(user=name)
    return (
        font("ADMIN REMINDER") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font(line) + "\n"
        + font("Action:") + " " + font("Message removed, no mute applied.")
    )


def review_text(name: str, count: int, muted: bool) -> str:
    action = f"Muted for {MUTE_MINUTES} minutes" if muted else "Mute failed; check AZAI permissions"
    return (
        font("ADMIN REVIEW REQUIRED") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("User:") + f" {name}\n"
        + font("Strike:") + f" {count}/{REVIEW_STRIKES}\n"
        + font("Action:") + f" {action}\n\n"
        + font("Owner/Admin, choose Ignore or Ban.")
    )


async def handle_abuse(event):
    sender = await event.get_sender()
    name = mention_user(sender, int(event.sender_id))
    admin_user = await is_admin(event)
    await safe_delete(event)

    if admin_user:
        await event.respond(admin_warning_text(name))
        await send_log(font("MOD LOG") + f"\nAdmin abuse reminder: {event.sender_id}\nChat: {event.chat_id}")
        return

    count = await add_strike(event.chat_id, event.sender_id, "abuse")
    muted = await mute_user(event, MUTE_MINUTES)

    if count >= REVIEW_STRIKES:
        await pending_db.update_one(
            {"chat_id": int(event.chat_id), "user_id": int(event.sender_id)},
            {"$set": {"chat_id": int(event.chat_id), "user_id": int(event.sender_id), "created_at": now_ist(), "status": "pending"}},
            upsert=True,
        )
        await event.respond(review_text(name, count, muted), buttons=review_buttons(event.chat_id, event.sender_id))
        await send_log(font("MOD LOG") + f"\nAbuse strike {count}: {event.sender_id}\nAction: review required")
        return

    await event.respond(user_warning_text(name, count, muted))
    await send_log(font("MOD LOG") + f"\nAbuse strike {count}: {event.sender_id}\nMuted: {muted}\nChat: {event.chat_id}")


async def handle_flood(event):
    key = (int(event.chat_id), int(event.sender_id))
    now = time.time()
    msg_cache[key].append(now)
    recent = [t for t in msg_cache[key] if now - t <= FLOOD_WINDOW_SECONDS]
    if len(recent) < FLOOD_LIMIT:
        return False
    await mute_user(event, MUTE_MINUTES)
    await safe_delete(event)
    await event.respond(font("CHAT LOCKED") + "\n\n" + font(f"Flood detected. Muted for {MUTE_MINUTES} minutes."))
    await send_log(font("MOD LOG") + f"\nFlood mute: {event.sender_id}\nChat: {event.chat_id}")
    msg_cache[key].clear()
    return True


async def handle_sticker_spam(event):
    if not getattr(event, "sticker", None):
        return False
    key = (int(event.chat_id), int(event.sender_id))
    now = time.time()
    sticker_cache[key].append(now)
    recent = [t for t in sticker_cache[key] if now - t <= STICKER_WINDOW_SECONDS]
    if len(recent) < STICKER_LIMIT:
        return False
    await mute_user(event, MUTE_MINUTES)
    await safe_delete(event)
    await event.respond(font("CHAT LOCKED") + "\n\n" + font(f"Sticker spam detected. Muted for {MUTE_MINUTES} minutes."))
    await send_log(font("MOD LOG") + f"\nSticker spam mute: {event.sender_id}\nChat: {event.chat_id}")
    sticker_cache[key].clear()
    return True


async def abuse_guard(event):
    if event.is_private or (event.is_channel and not event.is_group):
        return
    if not event.sender_id:
        return
    text = event.raw_text or ""
    if text.strip() and text.strip()[0] in prefix_cmds:
        return
    if await handle_sticker_spam(event):
        return
    if await handle_flood(event):
        return
    if text and ABUSE_RE.search(text):
        await handle_abuse(event)


async def abuse_review_callback(event):
    try:
        data = event.data.decode()
        action, chat_raw, user_raw = data.split("|")
        chat_id = int(chat_raw)
        user_id = int(user_raw)
    except Exception:
        await event.answer(font("Invalid review action."), alert=True)
        return
    if not await is_admin(event):
        await event.answer(font("Only admins can review this."), alert=True)
        return
    if action == "azab_ban":
        try:
            await event.client.edit_permissions(chat_id, user_id, view_messages=False)
            await pending_db.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"status": "banned", "reviewed_at": now_ist()}}, upsert=True)
            await event.edit(font("ACCESS DENIED") + "\n\n" + font("User banned by admin review."))
            await send_log(font("MOD LOG") + f"\nReview ban: {user_id}\nChat: {chat_id}")
        except Exception:
            await event.answer(font("Ban failed. Check permissions."), alert=True)
        return
    if action == "azab_ignore":
        await pending_db.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"status": "ignored", "reviewed_at": now_ist()}}, upsert=True)
        await abuse_db.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"count": 0, "updated_at": now_ist()}}, upsert=True)
        await event.edit(font("Review ignored. Strikes reset for this user."))
        return


if "azai_abuse_guard" not in tbot.handlers_loaded:
    tbot.add_event_handler(abuse_guard, events.NewMessage(incoming=True))
    tbot.add_event_handler(abuse_review_callback, events.CallbackQuery(pattern=b"^azab_"))
    tbot.handlers_loaded.add("azai_abuse_guard")
