from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

pic_db = database["azai_item_pics"]

ITEM_IDS = {
    "car_scorpio_s11_white",
    "car_scorpio_s11_black",
    "car_fortuner_black",
    "car_bmw_m5",
    "bike_splendor",
    "bike_duke_390",
    "bike_ninja_h2r",
    "rose",
    "chocolate",
    "ring",
    "teddy",
    "pizza",
    "surprise_box",
    "puppy",
    "cake",
    "letter",
    "cat",
    "tulip",
}


def owner_ids() -> set[int]:
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


async def is_owner(event) -> bool:
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


async def set_item_pic(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return

    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /setitempic item_id by replying to photo."))
        return

    item_id = parts[1].lower().strip().replace(" ", "_")
    if item_id not in ITEM_IDS:
        await event.reply(font("Unknown item id."))
        return

    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to item photo first."))
        return

    await pic_db.update_one(
        {"item_id": item_id},
        {"$set": {"item_id": item_id, "chat_id": int(reply.chat_id), "msg_id": int(reply.id)}},
        upsert=True,
    )
    await event.reply(font("Item photo saved:") + f" {item_id}")


if "aaa_azai_item_pics" not in tbot.handlers_loaded:
    tbot.add_event_handler(set_item_pic, events.NewMessage(pattern=f"^{prefix_cmds}setitempic(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("aaa_azai_item_pics")