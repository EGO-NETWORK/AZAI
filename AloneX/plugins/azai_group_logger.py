import os
from datetime import datetime

import pytz
from telethon import events, functions, types

from AloneX import database, font, prefix_cmds, tbot
import config

LOGGER_DB = database["azai_logger_settings"]
IST = pytz.timezone("Asia/Kolkata")


def owner_ids() -> set[int]:
    ids = set()
    for key in ("ALONE_OWNER_ID", "OWNER_ID", "SUDO_USERS", "OWNER_IDS"):
        value = getattr(config, key, None) or os.getenv(key)
        for part in str(value or "").replace(",", " ").split():
            try:
                if int(part):
                    ids.add(int(part))
            except Exception:
                pass
    return ids


def log_group_id():
    value = (
        getattr(config, "LOG_GROUP_ID", None)
        or getattr(config, "LOGGER_GROUP_ID", None)
        or os.getenv("LOG_GROUP_ID")
        or os.getenv("LOGGER_GROUP_ID")
        or os.getenv("LOGGER_ID")
    )
    try:
        return int(str(value).strip())
    except Exception:
        return None


def now_ist() -> str:
    return datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")


async def is_owner(event) -> bool:
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


async def logger_enabled() -> bool:
    row = await LOGGER_DB.find_one({"_id": "global"}) or {}
    return bool(row.get("enabled", True))


async def set_logger(enabled: bool, user_id: int = 0):
    await LOGGER_DB.update_one(
        {"_id": "global"},
        {"$set": {"enabled": bool(enabled), "updated_by": int(user_id or 0), "updated_at": now_ist()}},
        upsert=True,
    )


async def send_log(text: str):
    if not await logger_enabled():
        return
    chat_id = log_group_id()
    if not chat_id:
        return
    try:
        await tbot.send_message(chat_id, text, link_preview=False)
    except Exception as e:
        print(f"AZAI Logger Error: {e}")


def user_line(user):
    if not user:
        return "Unknown"
    name = " ".join(x for x in [getattr(user, "first_name", None), getattr(user, "last_name", None)] if x) or "Unknown"
    username = getattr(user, "username", None)
    uid = getattr(user, "id", None)
    return f"{name} (@{username}) | ID: {uid}" if username else f"{name} | ID: {uid}"


async def group_link(chat):
    username = getattr(chat, "username", None)
    if username:
        return f"https://t.me/{username}"
    try:
        invite = await tbot(functions.messages.ExportChatInviteRequest(chat))
        link = getattr(invite, "link", None)
        if link:
            return link
    except Exception:
        pass
    return "Not available. Make AZAI admin with invite-link permission."


async def logon_cmd(event):
    if not await is_owner(event):
        return
    sender = await event.get_sender()
    await set_logger(True, sender.id if sender else 0)
    await event.reply(font("Logger ON") + "\n" + font("Group/start logs will go to LOG_GROUP_ID."))


async def logoff_cmd(event):
    if not await is_owner(event):
        return
    sender = await event.get_sender()
    await set_logger(False, sender.id if sender else 0)
    await event.reply(font("Logger OFF"))


async def logstatus_cmd(event):
    if not await is_owner(event):
        return
    status = "ON" if await logger_enabled() else "OFF"
    await event.reply(
        font("LOGGER STATUS")
        + "\n━━━━━━━━━━━━━━━━━━\n"
        + font("Status:") + f" {status}\n"
        + font("LOG_GROUP_ID:") + f" {log_group_id() or 'Missing'}\n"
        + font("Commands:") + " /logon /logoff /logstatus"
    )


async def private_start_logger(event):
    if not event.is_private:
        return
    user = await event.get_sender()
    await send_log(
        "AZAI STARTED BY USER\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"User: {user_line(user)}\n"
        f"Time: {now_ist()}"
    )


async def log_group_snapshot(chat, added_by=None, title="AZAI GROUP LOGGER"):
    group_title = getattr(chat, "title", None) or "Unknown"
    cid = getattr(chat, "id", None)
    link = await group_link(chat)
    await send_log(
        f"{title}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"Group: {group_title}\n"
        f"Chat ID: {cid}\n"
        f"Link: {link}\n"
        f"Added By: {user_line(added_by)}\n"
        f"Time: {now_ist()}"
    )


async def group_add_logger(event):
    try:
        me = await tbot.get_me()
        user = await event.get_user()
        users = list(event.users) if getattr(event, "users", None) else ([user] if user else [])
        if not any(int(getattr(u, "id", 0)) == int(me.id) for u in users):
            return
        chat = await event.get_chat()
        added_by = None
        try:
            added_by = await event.get_added_by()
        except Exception:
            pass
        await log_group_snapshot(chat, added_by=added_by, title="AZAI ADDED TO GROUP")
    except Exception as e:
        print(f"AZAI Group Logger Error: {e}")


async def admin_update_logger(update):
    try:
        me = await tbot.get_me()
        if not isinstance(update, types.UpdateChannelParticipant):
            return
        if int(getattr(update, "user_id", 0) or 0) != int(me.id):
            return
        chat = await tbot.get_entity(types.PeerChannel(update.channel_id))
        await log_group_snapshot(chat, title="AZAI GROUP PERMISSION UPDATED")
    except Exception as e:
        print(f"AZAI Admin Logger Error: {e}")


if "azai_group_logger" not in tbot.handlers_loaded:
    tbot.add_event_handler(logon_cmd, events.NewMessage(pattern=f"^{prefix_cmds}logon(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(logoff_cmd, events.NewMessage(pattern=f"^{prefix_cmds}logoff(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(logstatus_cmd, events.NewMessage(pattern=f"^{prefix_cmds}logstatus(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(private_start_logger, events.NewMessage(pattern=f"^{prefix_cmds}start(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(group_add_logger, events.ChatAction())
    tbot.add_event_handler(admin_update_logger, events.Raw())
    tbot.handlers_loaded.add("azai_group_logger")
