import re
from datetime import datetime, timedelta

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
settings_db = database["azai_owner_override_mod"]

DEFAULT_MUTE_SECONDS = 10 * 60


def now_ist() -> str:
    return datetime.now(IST).strftime("%d %b %Y - %I:%M %p")


def owner_ids() -> set[int]:
    ids = set()
    for value in (OWNER_ID, ALONE_OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


def is_owner_id(user_id: int) -> bool:
    try:
        return int(user_id) in owner_ids()
    except Exception:
        return False


def parse_duration(text: str, default: int = DEFAULT_MUTE_SECONDS) -> int:
    text = str(text or "").strip().lower()
    match = re.search(r"\b(\d+)(s|m|h|d)\b", text)
    if not match:
        return default
    value = int(match.group(1))
    unit = match.group(2)
    if unit == "s":
        return max(value, 10)
    if unit == "m":
        return value * 60
    if unit == "h":
        return value * 3600
    if unit == "d":
        return value * 86400
    return default


def readable_duration(seconds: int) -> str:
    seconds = int(seconds)
    if seconds >= 86400 and seconds % 86400 == 0:
        return f"{seconds // 86400}d"
    if seconds >= 3600 and seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    if seconds >= 60 and seconds % 60 == 0:
        return f"{seconds // 60}m"
    return f"{seconds}s"


def user_name(user) -> str:
    return getattr(user, "first_name", None) or getattr(user, "username", None) or "User"


def mute_caption(user, duration: str) -> str:
    return (
        font("💀 Chat Locked") + "\n\n"
        + f"{user_name(user)} " + font("muted for") + f" {duration}\n"
        + font("Reason:") + " Owner override"
    )


def ban_caption(user) -> str:
    return (
        font("💀 Access Denied") + "\n\n"
        + f"{user_name(user)} " + font("banned from the group") + "\n"
        + font("Reason:") + " Owner override"
    )


async def enabled(chat_id: int) -> bool:
    row = await settings_db.find_one({"chat_id": int(chat_id)}) or {}
    return bool(row.get("enabled", False))


async def set_enabled(chat_id: int, value: bool, user_id: int):
    await settings_db.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"chat_id": int(chat_id), "enabled": bool(value), "updated_by": int(user_id), "updated_at": now_ist()}},
        upsert=True,
    )


def status_text(is_enabled: bool) -> str:
    return (
        font("OWNER OVERRIDE MOD") + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Status:") + f" {'ON' if is_enabled else 'OFF'}\n"
        + font("Owner Only:") + " MR EGO\n\n"
        + font("Use:") + " azai nikal / azai chup\n"
        + font("Target:") + " reply or @username"
    )


async def owner_mod_settings(event):
    if not event.sender_id or not is_owner_id(event.sender_id):
        return
    if event.is_private or (event.is_channel and not event.is_group):
        await event.reply(font("Use /ownermod inside a group."))
        return
    parts = (event.raw_text or "").split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else "status"
    if arg in {"on", "enable", "start"}:
        await set_enabled(event.chat_id, True, event.sender_id)
        await event.reply(status_text(True))
        return
    if arg in {"off", "disable", "stop"}:
        await set_enabled(event.chat_id, False, event.sender_id)
        await event.reply(status_text(False))
        return
    await event.reply(status_text(await enabled(event.chat_id)))


async def get_target(event):
    reply = await event.get_reply_message()
    if reply:
        sender = await reply.get_sender()
        if sender:
            return sender
    text = event.raw_text or ""
    match = re.search(r"@(\w{4,32})", text)
    if not match:
        return None
    try:
        return await event.client.get_entity(match.group(1))
    except Exception:
        return None


async def target_is_protected(event, target) -> bool:
    if not target:
        return True
    if getattr(target, "bot", False):
        return True
    if is_owner_id(getattr(target, "id", 0)):
        return True
    if int(target.id) == int(event.sender_id):
        return True
    try:
        perms = await event.client.get_permissions(event.chat_id, target.id)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


async def owner_phrase_handler(event):
    if event.is_private or (event.is_channel and not event.is_group):
        return
    if not event.sender_id or not is_owner_id(event.sender_id):
        return
    text = (event.raw_text or "").lower().strip()
    if not text or text[0] in prefix_cmds:
        return
    do_ban = "azai nikal" in text or "azai nikaal" in text or "azai bahar" in text
    do_mute = "azai chup" in text or "azai silent" in text or "azai mute" in text
    if not do_ban and not do_mute:
        return
    if not await enabled(event.chat_id):
        await event.reply(font("Owner Override Mod is OFF. Use /ownermod on first."))
        return
    target = await get_target(event)
    if not target:
        await event.reply(font("Reply to target user or tag @username first."))
        return
    if await target_is_protected(event, target):
        await event.reply(font("Protected target. AZAI will not take action on this user."))
        return
    if do_ban:
        try:
            await event.client.edit_permissions(event.chat_id, target.id, view_messages=False)
            await event.reply(ban_caption(target))
        except Exception:
            await event.reply(font("Ban failed. AZAI needs ban permission in this group."))
        return
    if do_mute:
        duration = parse_duration(text)
        try:
            until = datetime.utcnow() + timedelta(seconds=duration)
            await event.client.edit_permissions(event.chat_id, target.id, until_date=until, send_messages=False)
            await event.reply(mute_caption(target, readable_duration(duration)))
        except Exception:
            await event.reply(font("Mute failed. AZAI needs mute permission in this group."))
        return


if "azai_owner_override_mod" not in tbot.handlers_loaded:
    tbot.add_event_handler(owner_mod_settings, events.NewMessage(pattern=f"^{prefix_cmds}ownermod(?: .*)?$", incoming=True))
    tbot.add_event_handler(owner_phrase_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_owner_override_mod")
