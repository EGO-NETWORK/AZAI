from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

chat_db = database["azai_broadcast_chats"]


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
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


async def cache_chat(event):
    if event.fwd_from:
        return
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return
    chat_id = int(event.chat_id)
    ctype = "private" if event.is_private else "group"
    await chat_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, "type": ctype}},
        upsert=True,
    )


async def send_one(chat_id, text, pin=False):
    try:
        msg = await tbot.send_message(chat_id, text)
        if pin:
            try:
                await tbot.pin_message(chat_id, msg.id, notify=True)
            except Exception:
                pass
        return True
    except Exception:
        return False


async def broadcast_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /broadcast text"))
        return
    text = font("EGO NETWORK BROADCAST") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + raw[1]
    rows = await chat_db.find({}).to_list(length=5000)
    ok = 0
    fail = 0
    for row in rows:
        if await send_one(int(row["chat_id"]), text, False):
            ok += 1
        else:
            fail += 1
    await event.reply(font("Broadcast complete.") + f"\nSent: {ok}\nFailed: {fail}")


async def broadcast_pin_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /broadcastpin text"))
        return
    text = font("PINNED BROADCAST") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + raw[1]
    rows = await chat_db.find({}).to_list(length=5000)
    ok = 0
    fail = 0
    for row in rows:
        if await send_one(int(row["chat_id"]), text, True):
            ok += 1
        else:
            fail += 1
    await event.reply(font("Pinned broadcast complete where allowed.") + f"\nSent: {ok}\nFailed: {fail}\nPin needs admin right in groups.")


async def broadcast_stats(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    groups = await chat_db.count_documents({"type": "group"})
    private = await chat_db.count_documents({"type": "private"})
    await event.reply(font("Broadcast targets:") + f"\nGroups: {groups}\nDM users: {private}")


if "azai_broadcast" not in tbot.handlers_loaded:
    tbot.add_event_handler(broadcast_handler, events.NewMessage(pattern=f"^{prefix_cmds}broadcast(?: .*)?$", incoming=True))
    tbot.add_event_handler(broadcast_pin_handler, events.NewMessage(pattern=f"^{prefix_cmds}broadcastpin(?: .*)?$", incoming=True))
    tbot.add_event_handler(broadcast_stats, events.NewMessage(pattern=f"^{prefix_cmds}broadcaststats(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(cache_chat, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_broadcast")
