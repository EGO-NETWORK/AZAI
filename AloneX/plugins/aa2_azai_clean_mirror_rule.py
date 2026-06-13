import time
from datetime import datetime, timedelta

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
warn_db = database["azai_mirror_warnings"]


def owner_ids():
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            if int(value):
                ids.add(int(value))
        except Exception:
            pass
    return ids


def key(chat_id, user_id):
    return {"chat_id": int(chat_id), "user_id": int(user_id)}


def bad_tone(text):
    try:
        from AloneX.plugins import zzzz_azai_mirror_rule as old
        return old.bad_tone(text)
    except Exception:
        return False


def display_name(user):
    if not user:
        return font("Member")
    name = " ".join(x for x in [getattr(user, "first_name", None), getattr(user, "last_name", None)] if x).strip()
    username = getattr(user, "username", None)
    if name and username:
        return f"{font(name)} (@{username})"
    return f"@{username}" if username else font(name or "Member")


async def count(chat_id, user_id):
    data = await warn_db.find_one(key(chat_id, user_id))
    return int((data or {}).get("count", 0))


def warning_text(user, num):
    return (
        font("AZAI MIRROR RULE")
        + "\n━━━━━━━━━━━━━━━━━━━━\n"
        + font("Member:") + " " + display_name(user) + "\n"
        + font("Warning:") + f" {num}/3\n\n"
        + font("Mirror response active. Keep your tone clean, controlled, and respectful.") + "\n"
        + font("Respect the room and the room respects you.")
    )


async def clean_mirror_handler(event):
    if event.is_private or event.fwd_from:
        return
    text = event.raw_text or ""
    if not text or text[0] in prefix_cmds:
        return
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False) or int(sender.id) in owner_ids():
        return
    if not bad_tone(text):
        return
    try:
        await event.delete()
    except Exception:
        pass
    num = await count(event.chat_id, sender.id) + 1
    await warn_db.update_one(key(event.chat_id, sender.id), {"$set": {**key(event.chat_id, sender.id), "count": num, "updated_at": int(time.time())}}, upsert=True)
    if num <= 3:
        await event.respond(warning_text(sender, num))
    else:
        try:
            until = datetime.now(IST) + timedelta(minutes=30)
            await tbot.edit_permissions(event.chat_id, sender.id, until_date=until, send_messages=False)
            await event.respond(font("AZAI MIRROR RULE") + "\n━━━━━━━━━━━━━━━━━━━━\n" + display_name(sender) + " " + font("crossed 3 mirror warnings and has been muted for 30 minutes."))
        except Exception:
            await event.respond(font("Mirror limit crossed. Admin mute permission is required for action."))
    raise events.StopPropagation


if "aa2_azai_clean_mirror_rule" not in tbot.handlers_loaded:
    tbot.add_event_handler(clean_mirror_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("aa2_azai_clean_mirror_rule")
