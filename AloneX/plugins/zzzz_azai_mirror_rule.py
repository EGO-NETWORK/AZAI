import time
from datetime import datetime, timedelta

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
warn_db = database["azai_mirror_warnings"]
BAD_PARTS = ["bs" + "dk", "mc", "bc", "bkl", "ch" + "uti", "madar", "bhen", "gali", "abuse"]


def owner_ids():
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            if int(value):
                ids.add(int(value))
        except Exception:
            pass
    return ids


async def is_owner_user(user_id: int) -> bool:
    return int(user_id) in owner_ids()


def key(chat_id: int, user_id: int):
    return {"chat_id": int(chat_id), "user_id": int(user_id)}


def bad_tone(text: str) -> bool:
    low = (text or "").lower()
    return any(x in low for x in BAD_PARTS)


def display_name(user):
    if not user:
        return font("Member")
    name = " ".join(x for x in [getattr(user, "first_name", None), getattr(user, "last_name", None)] if x).strip()
    username = getattr(user, "username", None)
    if name and username:
        return f"{font(name)} (@{username})"
    return f"@{username}" if username else font(name or "Member")


async def warn_count(chat_id: int, user_id: int) -> int:
    data = await warn_db.find_one(key(chat_id, user_id))
    return int((data or {}).get("count", 0))


async def mirror_handler(event):
    if event.is_private or event.fwd_from:
        return
    text = event.raw_text or ""
    if not text or text[0] in prefix_cmds:
        return
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False) or await is_owner_user(sender.id):
        return
    if not bad_tone(text):
        return

    try:
        await event.delete()
    except Exception:
        pass

    current = await warn_count(event.chat_id, sender.id)
    new_count = current + 1
    await warn_db.update_one(key(event.chat_id, sender.id), {"$set": {**key(event.chat_id, sender.id), "count": new_count, "updated_at": int(time.time())}}, upsert=True)

    if new_count <= 3:
        text = (
            font("AZAI MIRROR RULE") + "\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            + font("Member:") + " " + display_name(sender) + "\n"
            + font("Warning:") + f" {new_count}/3\n\n"
            + font("Clean language required. Respect doge to respect milega.")
        )
        await event.respond(text)
    else:
        try:
            until = datetime.now(IST) + timedelta(minutes=30)
            await tbot.edit_permissions(event.chat_id, sender.id, until_date=until, send_messages=False)
            await event.respond(font("AZAI MIRROR RULE") + "\n━━━━━━━━━━━━━━━━━━━━\n" + display_name(sender) + " " + font("muted for 30 minutes."))
        except Exception:
            await event.respond(font("Mute failed. Admin permission needed."))
    raise events.StopPropagation


async def abusewarns(event):
    if event.is_private:
        return
    sender = await event.get_sender()
    if not sender or not await is_owner_user(sender.id):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    reply = await event.get_reply_message()
    target = await reply.get_sender() if reply else sender
    count = await warn_count(event.chat_id, target.id)
    await event.reply(font("Mirror warnings:") + f" {count}")
    raise events.StopPropagation


async def resetabuse(event):
    if event.is_private:
        return
    sender = await event.get_sender()
    if not sender or not await is_owner_user(sender.id):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to user first."))
        raise events.StopPropagation
    target = await reply.get_sender()
    await warn_db.delete_one(key(event.chat_id, target.id))
    await event.reply(font("Mirror warnings reset."))
    raise events.StopPropagation


if "zzzz_azai_mirror_rule" not in tbot.handlers_loaded:
    tbot.add_event_handler(abusewarns, events.NewMessage(pattern=f"^{prefix_cmds}abusewarns$", incoming=True))
    tbot.add_event_handler(resetabuse, events.NewMessage(pattern=f"^{prefix_cmds}resetabuse$", incoming=True))
    tbot.add_event_handler(mirror_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("zzzz_azai_mirror_rule")
