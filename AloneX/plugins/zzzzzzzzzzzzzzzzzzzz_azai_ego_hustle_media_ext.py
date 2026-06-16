from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

media_db = database["azai_game_media"]

MEDIA_KEYS = {
    "sethustlepic": "game",
    "setgamepic": "game",
    "setwalletpic": "wallet",
    "setbalpic": "wallet",
    "setdailypic": "daily",
    "setworkpic": "work",
    "setluckpic": "luck",
    "setprotectpic": "protect",
    "setraidpic": "raid",
    "setattackpic": "attack",
    "setheistpic": "heist",
    "setleaderboardpic": "leaderboard",
    "setrankpic": "leaderboard",
    "setprofilepic": "profile",
    "setgameprofilepic": "profile",
}


def _safe_int(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def owner_ids():
    return {x for x in {_safe_int(ALONE_OWNER_ID), _safe_int(OWNER_ID)} if x}


async def is_owner(event):
    return int(event.sender_id or 0) in owner_ids()


async def save_feature_media(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation

    cmd = (event.raw_text or "").split()[0].lstrip("/!.").lower()
    key = MEDIA_KEYS.get(cmd)
    if not key:
        return

    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to an image/video/document first."))
        raise events.StopPropagation

    await media_db.update_one(
        {"key": key},
        {"$set": {"key": key, "chat_id": int(reply.chat_id), "msg_id": int(reply.id)}},
        upsert=True,
    )
    await event.reply(font("EGO Hustle image saved:") + f" {key}")
    raise events.StopPropagation


async def media_list(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    rows = await media_db.find({}).to_list(length=100)
    saved = {row.get("key") for row in rows}
    text = font("EGO HUSTLE MEDIA") + "\n━━━━━━━━━━━━━━━━━━━━"
    for key in ["game", "wallet", "daily", "work", "luck", "protect", "raid", "attack", "heist", "leaderboard", "profile"]:
        mark = "✅" if key in saved else "❌"
        text += f"\n{mark} {key}"
    await event.reply(text)
    raise events.StopPropagation


if "zzzzzzzzzzzzzzzzzzzz_azai_ego_hustle_media_ext" not in tbot.handlers_loaded:
    pattern = "|".join(MEDIA_KEYS.keys())
    tbot.add_event_handler(save_feature_media, events.NewMessage(pattern=f"^{prefix_cmds}({pattern})(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(media_list, events.NewMessage(pattern=f"^{prefix_cmds}(egohmedia|hustlemedia)(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzz_azai_ego_hustle_media_ext")
