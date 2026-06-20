import os
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


def strike_text(count: int, action: str) -> str:
    return (
        font("AZAI MODERATION") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Message removed:") + " " + font("Group rule violation") + "\n"
        + font("Strike:") + f" {count}/3\n"
        + font("Action:") + f" {action}"
    )


def review_buttons(chat_id: int, user_id: int):
    return [[
        Button.inline(font("Ban"), f"azab_ban|{chat_id}|{user_id}".encode()),
        Button.inline(font("Ignore"), f"azab_ignore|{chat_id}|{user_id}".encode()),
    ]]


async def handle_abuse(event):
    count = await add_strike(event.chat_id, event.sender_id, "abuse")
    await safe_delete(event)
    if count == 1:
        await event.respond(strike_text(count, "Warning"))
        await send_log(font("MOD LOG") + f"\nAbuse strike 1: {event.sender_id}\nChat: {event.chat_id}")
        return
    if count == 2:
        muted = await mute_user(event, 10)
        action = "Muted for 10 minutes" if muted else "Mute failed; check admin permissions"
        await event.respond(strike_text(count, action))
        await send_log(font("MOD LOG") + f"\nAbuse strike 2: {event.sender_id}\nAction: {action}")
        return
    muted = await mute_user(event, 60)
    action = "Muted for 60 minutes; admin review required" if muted else "Admin review required; mute failed"
    await pending_db.update_one(
        {"chat_id": int(event.chat_id), "user_id": int(event.sender_id)},
        {"$set": {"chat_id": int(event.chat_id), "user_id": int(event.sender_id), "created_at": now_ist(), "status": "pending"}},
        upsert=True,
    )
    await event.respond(strike_text(count, action), buttons=review_buttons(event.chat_id, event.sender_id))
    await send_log(font("MOD LOG") + f"\nAbuse strike {count}: {event.sender_id}\nAction: {action}")


async def handle_flood(event):
    key = (int(event.chat_id), int(event.sender_id))
    now = time.time()
    msg_cache[key].append(now)
    recent = [t for t in msg_cache[key] if now - t <= FLOOD_WINDOW_SECONDS]
    if len(recent) < FLOOD_LIMIT:
        return False
    await mute_user(event, 10)
    await safe_delete(event)
    await event.respond(font("Flood detected. User muted for 10 minutes."))
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
    await mute_user(event, 10)
    await safe_delete(event)
    await event.respond(font("Sticker spam detected. User muted for 10 minutes."))
    await send_log(font("MOD LOG") + f"\nSticker spam mute: {event.sender_id}\nChat: {event.chat_id}")
    sticker_cache[key].clear()
    return True


async def abuse_guard(event):
    if event.is_private or (event.is_channel and not event.is_group):
        return
    if not event.sender_id or await is_admin(event):
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
            await event.edit(font("User banned by admin review."))
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
    tbot.add_event_handler(abuse_guard, events.NewMessage(incoming=True), group=-80)
    tbot.add_event_handler(abuse_review_callback, events.CallbackQuery(pattern=b"^azab_"))
    tbot.handlers_loaded.add("azai_abuse_guard")
