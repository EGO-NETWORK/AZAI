from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
media_db = database["azai_game_media"]
COMMANDS = {"setattackpic": "attack", "setraidpic": "raid", "setheistpic": "heist"}


def now_ist():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def owner_ids():
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


async def is_owner(event):
    user = await event.get_sender()
    return bool(user and int(user.id) in owner_ids())


async def media_cmd(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    cmd = (event.raw_text or "").split()[0].lstrip("/!.").lower()
    key = COMMANDS.get(cmd)
    if not key:
        return
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to media first."))
        raise events.StopPropagation
    await media_db.update_one({"key": key}, {"$set": {"key": key, "chat_id": int(reply.chat_id), "msg_id": int(reply.id), "updated_at": now_ist()}}, upsert=True)
    await event.reply(font("EGO Hustle media saved:") + f" {key}")
    raise events.StopPropagation


if "zzzz_azai_ego_hustle_media_extra" not in tbot.handlers_loaded:
    tbot.add_event_handler(media_cmd, events.NewMessage(pattern=f"^{prefix_cmds}(setattackpic|setraidpic|setheistpic)$", incoming=True))
    tbot.handlers_loaded.add("zzzz_azai_ego_hustle_media_extra")
