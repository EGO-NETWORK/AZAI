import random
import re
import time

from telethon import events, functions, types

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

sticker_db = database["azai_sticker_packs"]
sticker_cooldown = {}
AUTO_REPLY_COOLDOWN = 4


def owner_ids() -> set[int]:
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            if int(value):
                ids.add(int(value))
        except Exception:
            pass
    return ids


async def is_owner_or_admin(event) -> bool:
    sender = await event.get_sender()
    if not sender:
        return False
    if int(sender.id) in owner_ids():
        return True
    if event.is_private:
        return False
    try:
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


def clean_pack_name(value: str) -> str:
    value = str(value or "").strip()
    value = value.replace("https://t.me/addstickers/", "")
    value = value.replace("http://t.me/addstickers/", "")
    value = value.replace("t.me/addstickers/", "")
    value = value.strip("/")
    value = re.sub(r"[^A-Za-z0-9_]+", "", value)
    return value


def clean_mood(value: str) -> str:
    value = str(value or "default").strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "", value)
    return value or "default"


async def save_pack(chat_id: int, pack: str, mood: str):
    await sticker_db.update_one({"chat_id": chat_id, "pack": pack}, {"$set": {"chat_id": chat_id, "pack": pack, "mood": mood}}, upsert=True)


async def remove_pack(chat_id: int, pack: str) -> int:
    result = await sticker_db.delete_many({"chat_id": chat_id, "pack": pack})
    return result.deleted_count


async def list_packs(chat_id: int) -> list[dict]:
    cursor = sticker_db.find({"chat_id": chat_id})
    return [item async for item in cursor]


async def mood_packs(chat_id: int, mood: str) -> list[str]:
    cursor = sticker_db.find({"chat_id": chat_id, "mood": mood})
    return [item["pack"] async for item in cursor if item.get("pack")]


async def random_sticker_from_pack(pack: str):
    try:
        sticker_set = await tbot(functions.messages.GetStickerSetRequest(stickerset=types.InputStickerSetShortName(pack), hash=0))
        docs = list(getattr(sticker_set, "documents", []) or [])
        if not docs:
            return None
        return random.choice(docs)
    except Exception:
        return None


def sticker_help_text() -> str:
    return (
        font("AZAI STICKER CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Access:") + " " + font("Group Admin / Bot Owner") + "\n\n"
        + font("Commands:") + "\n"
        + "/stickerpack add <pack> <mood>\n"
        + "/stickerpack remove <pack>\n"
        + "/stickerpack list\n"
        + "/stickermood <mood>\n\n"
        + font("Example:") + "\n"
        + "/stickerpack add https://t.me/addstickers/PackName happy\n"
        + "/stickermood happy\n\n"
        + font("Powered By:") + " " + font("EGO Network - EST. 2026")
    )


async def stickerpack_handler(event):
    if not await is_owner_or_admin(event):
        await event.reply(font("Group admin only."))
        raise events.StopPropagation
    text = (event.raw_text or "").strip()
    parts = text.split()
    if len(parts) < 2:
        await event.reply(sticker_help_text())
        raise events.StopPropagation
    action = parts[1].lower()
    chat_id = event.chat_id
    if action == "add":
        if len(parts) < 3:
            await event.reply(font("Use: /stickerpack add <pack_link_or_name> <mood>"))
            raise events.StopPropagation
        pack = clean_pack_name(parts[2])
        mood = clean_mood(parts[3] if len(parts) > 3 else "default")
        if not pack:
            await event.reply(font("Sticker pack name is invalid."))
            raise events.StopPropagation
        await save_pack(chat_id, pack, mood)
        await event.reply(font("Sticker pack added.") + "\n" + font("Mood:") + f" {mood}\n" + font("Pack:") + f" {pack}")
        raise events.StopPropagation
    if action in {"remove", "del", "delete"}:
        if len(parts) < 3:
            await event.reply(font("Use: /stickerpack remove <pack_name>"))
            raise events.StopPropagation
        pack = clean_pack_name(parts[2])
        count = await remove_pack(chat_id, pack)
        await event.reply(font("Sticker pack removed:") + f" {count}")
        raise events.StopPropagation
    if action == "list":
        packs = await list_packs(chat_id)
        if not packs:
            await event.reply(font("No sticker packs added yet."))
            raise events.StopPropagation
        lines = [font("AZAI STICKER PACKS"), "━━━━━━━━━━━━━━━━━━━━━━━━━━━━", ""]
        for item in packs[:30]:
            lines.append(f"{item.get('mood', 'default')} - {item.get('pack')}")
        await event.reply("\n".join(lines))
        raise events.StopPropagation
    await event.reply(sticker_help_text())
    raise events.StopPropagation


async def stickermood_handler(event):
    if not await is_owner_or_admin(event):
        await event.reply(font("Group admin only."))
        raise events.StopPropagation
    parts = (event.raw_text or "").split()
    mood = clean_mood(parts[1] if len(parts) > 1 else "default")
    packs = await mood_packs(event.chat_id, mood)
    if not packs:
        await event.reply(font("No sticker pack found for this mood."))
        raise events.StopPropagation
    sticker = await random_sticker_from_pack(random.choice(packs))
    if not sticker:
        await event.reply(font("Could not load sticker from saved packs."))
        raise events.StopPropagation
    await event.reply(file=sticker)
    raise events.StopPropagation


async def sticker_echo_handler(event):
    if event.fwd_from:
        return
    sticker = getattr(event.message, "sticker", None)
    if not sticker:
        return
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return
    cd_key = (event.chat_id, sender.id)
    now = time.time()
    if sticker_cooldown.get(cd_key, 0) + AUTO_REPLY_COOLDOWN > now:
        return
    sticker_cooldown[cd_key] = now
    try:
        await event.reply(file=sticker)
    except Exception:
        pass


if "azai_stickers" not in tbot.handlers_loaded:
    tbot.add_event_handler(stickerpack_handler, events.NewMessage(pattern=f"^{prefix_cmds}stickerpack(?: .*)?$", incoming=True))
    tbot.add_event_handler(stickermood_handler, events.NewMessage(pattern=f"^{prefix_cmds}stickermood(?: .*)?$", incoming=True))
    tbot.add_event_handler(sticker_echo_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_stickers")
