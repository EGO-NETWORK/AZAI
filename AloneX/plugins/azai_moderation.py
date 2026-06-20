import os
import re
from datetime import datetime, timedelta

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
mod_db = database["azai_moderation"]
warn_db = database["azai_warnings"]

LINK_RE = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/|telegram\.dog/)", re.IGNORECASE)
DEFAULT_MAX_WARNS = 3
DEFAULT_MUTE_SECONDS = 10 * 60
MAX_PURGE_LIMIT = 100


def now_text() -> str:
    return datetime.now(IST).strftime("%d %b %Y - %I:%M %p")


def parse_duration(text: str, default: int = DEFAULT_MUTE_SECONDS) -> int:
    text = str(text or "").strip().lower()
    if not text:
        return default
    match = re.match(r"^(\d+)(s|m|h|d)?$", text)
    if not match:
        return default
    value = int(match.group(1))
    unit = match.group(2) or "m"
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


def mute_caption(user, duration: str, reason: str = "Admin action") -> str:
    return (
        font("💀 Chat Locked") + "\n\n"
        + f"{user_name(user)} " + font("muted for") + f" {duration}\n"
        + font("Reason:") + f" {reason}"
    )


def ban_caption(user, reason: str = "Admin action") -> str:
    return (
        font("💀 Access Denied") + "\n\n"
        + f"{user_name(user)} " + font("banned from the group") + "\n"
        + font("Reason:") + f" {reason}"
    )


def kick_caption(user, reason: str = "Admin action") -> str:
    return (
        font("💀 Access Removed") + "\n\n"
        + f"{user_name(user)} " + font("kicked from the group") + "\n"
        + font("Reason:") + f" {reason}"
    )


async def send_mod_log(chat_id: int, text: str):
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


async def is_group_admin(event) -> bool:
    if event.is_private:
        await event.reply(font("This command works only inside groups."))
        return False
    if event.is_channel and not event.is_group:
        return False
    try:
        sender = await event.get_sender()
        if getattr(sender, "bot", False):
            return True
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


async def require_admin(event) -> bool:
    ok = await is_group_admin(event)
    if not ok:
        await event.reply(font("Only group admins can use this command."))
    return ok


async def target_from_reply(event):
    reply = await event.get_reply_message()
    if not reply:
        return None
    return await reply.get_sender()


async def settings(chat_id: int) -> dict:
    data = await mod_db.find_one({"chat_id": chat_id}) or {}
    return {"antilink": bool(data.get("antilink", False)), "max_warns": int(data.get("max_warns", DEFAULT_MAX_WARNS))}


async def set_setting(chat_id: int, key: str, value):
    await mod_db.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)


async def warn_count(chat_id: int, user_id: int) -> int:
    data = await warn_db.find_one({"chat_id": chat_id, "user_id": user_id}) or {}
    return int(data.get("count", 0))


async def add_warn(chat_id: int, user_id: int, reason: str) -> int:
    await warn_db.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"count": 1}, "$set": {"last_reason": reason, "updated_at": now_text()}, "$setOnInsert": {"chat_id": chat_id, "user_id": user_id, "created_at": now_text()}},
        upsert=True,
    )
    return await warn_count(chat_id, user_id)


async def reset_warn(chat_id: int, user_id: int):
    await warn_db.delete_one({"chat_id": chat_id, "user_id": user_id})


def mod_home_text(current: dict) -> str:
    antilink = font("ON") if current.get("antilink") else font("OFF")
    return (
        font("AZAI MODERATION PANEL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Anti-Link:") + f" {antilink}\n"
        + font("Max Warnings:") + f" {current.get('max_warns', DEFAULT_MAX_WARNS)}\n\n"
        + font("Commands:") + " /warn /mute /ban /kick /purge /antilink\n"
        + font("Caption Style:") + " 💀 compact\n\n"
        + font("Powered By:") + " " + BRAND
    )


def mod_help_text() -> str:
    return (
        font("MODERATION COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/mod - " + font("Open moderation panel") + "\n"
        + "/warn - " + font("Warn replied user") + "\n"
        + "/unwarn - " + font("Remove one warning") + "\n"
        + "/warnings - " + font("Check warnings") + "\n"
        + "/resetwarns - " + font("Reset warnings") + "\n"
        + "/mute 10m - " + font("Mute replied user") + "\n"
        + "/unmute - " + font("Unmute replied user") + "\n"
        + "/ban - " + font("Ban replied user") + "\n"
        + "/unban - " + font("Unban replied user") + "\n"
        + "/kick - " + font("Kick replied user") + "\n"
        + "/purge - " + font("Delete messages from replied message to command") + "\n"
        + "/antilink on/off - " + font("Toggle link protection") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def mod_buttons(current: dict):
    antilink_label = font("Anti-Link ON") if current.get("antilink") else font("Anti-Link OFF")
    return [[Button.inline(antilink_label, b"azmod_toggle_antilink")], [Button.inline(font("Commands"), b"azmod_help"), Button.inline(font("Refresh"), b"azmod_home")], [Button.inline(font("Close"), b"azmod_close")]]


async def mod_panel(event):
    if not await require_admin(event):
        return
    current = await settings(event.chat_id)
    await event.reply(mod_home_text(current), buttons=mod_buttons(current))


async def antilink_handler(event):
    if not await require_admin(event):
        return
    parts = (event.raw_text or "").split()
    if len(parts) < 2 or parts[1].lower() not in {"on", "off"}:
        await event.reply(font("Use: /antilink on or /antilink off"))
        return
    enabled = parts[1].lower() == "on"
    await set_setting(event.chat_id, "antilink", enabled)
    await event.reply(font("Anti-Link set to:") + " " + (font("ON") if enabled else font("OFF")))


async def warn_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to a user and use /warn."))
        return
    if getattr(target, "bot", False):
        await event.reply(font("Bots cannot be warned here."))
        return
    reason = " ".join((event.raw_text or "").split()[1:]) or "No reason added"
    current = await settings(event.chat_id)
    count = await add_warn(event.chat_id, target.id, reason)
    text = font("💀 AZAI Saw That") + "\n\n" + font("Strike:") + f" {count}/{current['max_warns']}\n" + font("Warning")
    await event.reply(text)
    await send_mod_log(event.chat_id, font("MOD LOG") + f"\nWarned: {target.id}\nReason: {reason}")
    if count >= current["max_warns"]:
        try:
            duration = DEFAULT_MUTE_SECONDS
            until = datetime.utcnow() + timedelta(seconds=duration)
            await event.client.edit_permissions(event.chat_id, target.id, until_date=until, send_messages=False)
            await event.reply(mute_caption(target, readable_duration(duration), "warning limit"))
        except Exception:
            await event.reply(font("Warning limit reached, but mute failed. Check bot admin permissions."))


async def warnings_handler(event):
    target = await target_from_reply(event) or await event.get_sender()
    count = await warn_count(event.chat_id, target.id)
    await event.reply(font("Warnings:") + f" {count}/{DEFAULT_MAX_WARNS}")


async def resetwarns_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to a user and use /resetwarns."))
        return
    await reset_warn(event.chat_id, target.id)
    await event.reply(font("Warnings reset."))


async def unwarn_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to a user and use /unwarn."))
        return
    count = max(await warn_count(event.chat_id, target.id) - 1, 0)
    await warn_db.update_one({"chat_id": event.chat_id, "user_id": target.id}, {"$set": {"count": count}}, upsert=True)
    await event.reply(font("One warning removed. Current warnings:") + f" {count}")


async def mute_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to a user and use /mute 10m."))
        return
    parts = (event.raw_text or "").split()
    duration = parse_duration(parts[1] if len(parts) > 1 else "10m")
    reason = " ".join(parts[2:]) if len(parts) > 2 else "Admin action"
    try:
        until = datetime.utcnow() + timedelta(seconds=duration)
        await event.client.edit_permissions(event.chat_id, target.id, until_date=until, send_messages=False)
        await event.reply(mute_caption(target, readable_duration(duration), reason))
        await send_mod_log(event.chat_id, font("MOD LOG") + f"\nMuted: {target.id}\nDuration: {readable_duration(duration)}")
    except Exception:
        await event.reply(font("Mute failed. Check bot admin permissions."))


async def unmute_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to a user and use /unmute."))
        return
    try:
        await event.client.edit_permissions(event.chat_id, target.id, send_messages=True)
        await event.reply(font("User unmuted."))
    except Exception:
        await event.reply(font("Unmute failed. Check bot admin permissions."))


async def ban_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to a user and use /ban."))
        return
    parts = (event.raw_text or "").split()
    reason = " ".join(parts[1:]) if len(parts) > 1 else "Admin action"
    try:
        await event.client.edit_permissions(event.chat_id, target.id, view_messages=False)
        await event.reply(ban_caption(target, reason))
        await send_mod_log(event.chat_id, font("MOD LOG") + f"\nBanned: {target.id}")
    except Exception:
        await event.reply(font("Ban failed. Check bot admin permissions."))


async def unban_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to the user's old message and use /unban, or unban manually from Telegram settings."))
        return
    try:
        await event.client.edit_permissions(event.chat_id, target.id, view_messages=True)
        await event.reply(font("User unbanned."))
    except Exception:
        await event.reply(font("Unban failed. Check bot admin permissions."))


async def kick_handler(event):
    if not await require_admin(event):
        return
    target = await target_from_reply(event)
    if not target:
        await event.reply(font("Reply to a user and use /kick."))
        return
    try:
        await event.client.edit_permissions(event.chat_id, target.id, view_messages=False)
        await event.client.edit_permissions(event.chat_id, target.id, view_messages=True)
        await event.reply(kick_caption(target, "Admin action"))
        await send_mod_log(event.chat_id, font("MOD LOG") + f"\nKicked: {target.id}")
    except Exception:
        await event.reply(font("Kick failed. Check bot admin permissions."))


async def purge_handler(event):
    if not await require_admin(event):
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to the first message and use /purge."))
        return
    start_id = int(reply.id)
    end_id = int(event.id)
    if end_id < start_id:
        await event.reply(font("Invalid purge range."))
        return
    ids = list(range(start_id, end_id + 1))[:MAX_PURGE_LIMIT]
    try:
        await event.client.delete_messages(event.chat_id, ids)
        await event.client.send_message(event.chat_id, font("💀 Cleaned") + "\n\n" + font("Purged messages:") + f" {len(ids)}")
        await send_mod_log(event.chat_id, font("MOD LOG") + f"\nPurged: {len(ids)} messages")
    except Exception:
        await event.reply(font("Purge failed. Check bot admin permissions."))


async def mod_callback(event):
    try:
        sender = await event.get_sender()
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        allowed = bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        allowed = False
    if not allowed:
        await event.answer(font("Only group admins can use this panel."), alert=True)
        return
    data = event.data.decode()
    current = await settings(event.chat_id)
    if data == "azmod_toggle_antilink":
        await set_setting(event.chat_id, "antilink", not current.get("antilink"))
        current = await settings(event.chat_id)
        await event.edit(mod_home_text(current), buttons=mod_buttons(current))
    elif data == "azmod_help":
        await event.edit(mod_help_text(), buttons=[[Button.inline(font("Back"), b"azmod_home"), Button.inline(font("Close"), b"azmod_close")]])
    elif data == "azmod_home":
        await event.edit(mod_home_text(current), buttons=mod_buttons(current))
    elif data == "azmod_close":
        await event.delete()


async def antilink_guard(event):
    if event.is_private or (event.is_channel and not event.is_group):
        return
    text = event.raw_text or ""
    if not LINK_RE.search(text):
        return
    current = await settings(event.chat_id)
    if not current.get("antilink"):
        return
    if await is_group_admin(event):
        return
    try:
        await event.delete()
    except Exception:
        pass
    try:
        await event.respond(font("💀 Link Removed") + "\n\n" + font("Group protection is active."))
        await send_mod_log(event.chat_id, font("MOD LOG") + f"\nLink removed from user: {event.sender_id}")
    except Exception:
        pass


if "azai_moderation" not in tbot.handlers_loaded:
    tbot.add_event_handler(mod_panel, events.NewMessage(pattern=f"^{prefix_cmds}mod$", incoming=True))
    tbot.add_event_handler(antilink_handler, events.NewMessage(pattern=f"^{prefix_cmds}antilink(?: .*)?$", incoming=True))
    tbot.add_event_handler(warn_handler, events.NewMessage(pattern=f"^{prefix_cmds}warn(?: .*)?$", incoming=True))
    tbot.add_event_handler(unwarn_handler, events.NewMessage(pattern=f"^{prefix_cmds}unwarn$", incoming=True))
    tbot.add_event_handler(warnings_handler, events.NewMessage(pattern=f"^{prefix_cmds}warnings$", incoming=True))
    tbot.add_event_handler(resetwarns_handler, events.NewMessage(pattern=f"^{prefix_cmds}resetwarns$", incoming=True))
    tbot.add_event_handler(mute_handler, events.NewMessage(pattern=f"^{prefix_cmds}mute(?: .*)?$", incoming=True))
    tbot.add_event_handler(unmute_handler, events.NewMessage(pattern=f"^{prefix_cmds}unmute$", incoming=True))
    tbot.add_event_handler(ban_handler, events.NewMessage(pattern=f"^{prefix_cmds}ban(?: .*)?$", incoming=True))
    tbot.add_event_handler(unban_handler, events.NewMessage(pattern=f"^{prefix_cmds}unban$", incoming=True))
    tbot.add_event_handler(kick_handler, events.NewMessage(pattern=f"^{prefix_cmds}kick$", incoming=True))
    tbot.add_event_handler(purge_handler, events.NewMessage(pattern=f"^{prefix_cmds}purge$", incoming=True))
    tbot.add_event_handler(mod_callback, events.CallbackQuery(pattern=b"^azmod_"))
    tbot.add_event_handler(antilink_guard, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_moderation")
