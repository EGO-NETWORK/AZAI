from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")

wallet_db = database["azai_wallets"]
pic_db = database["azai_item_pics"]

CURRENCY = "EC"

GIFTS = {
    "rose": {"name": "Rose", "price": 500},
    "chocolate": {"name": "Chocolate", "price": 800},
    "ring": {"name": "Ring", "price": 2000},
    "teddy": {"name": "Teddy Bear", "price": 1500},
    "pizza": {"name": "Pizza", "price": 600},
    "surprise_box": {"name": "Surprise Box", "price": 2500},
    "puppy": {"name": "Puppy", "price": 3000},
    "cake": {"name": "Cake", "price": 1000},
    "letter": {"name": "Letter", "price": 400},
    "cat": {"name": "Cat", "price": 2500},
    "tulip": {"name": "Tulip", "price": 1500},
}

ALIASES = {
    "teddy_bear": "teddy",
    "bear": "teddy",
    "surprise": "surprise_box",
    "surprisebox": "surprise_box",
    "box": "surprise_box",
    "note": "letter",
    "message": "letter",
}


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


def item_key(raw):
    key = (raw or "").lower().strip().replace(" ", "_").replace("-", "_")
    return ALIASES.get(key, key)


def user_name(user):
    if not user:
        return "User"

    try:
        if int(user.id) in owner_ids():
            return "MR EGO"
    except Exception:
        pass

    name = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
    username = getattr(user, "username", None)

    if username:
        return f"{name} (@{username})"

    return name


async def get_wallet(user_id):
    user_id = int(user_id)

    data = await wallet_db.find_one({"user_id": user_id})
    if not data:
        data = {
            "user_id": user_id,
            "balance": 0,
            "gifts": [],
            "created_at": now_ist(),
        }
        await wallet_db.insert_one(data)

    return data


async def get_item_media(item_id):
    data = await pic_db.find_one({"item_id": item_id})
    if not data:
        return None

    try:
        msg = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        if msg and msg.media:
            return msg.media
    except Exception:
        return None

    return None


async def gift_handler(event):
    reply = await event.get_reply_message()

    if not reply:
        await event.reply(font("Reply to a user message and use /gift item_id."))
        raise events.StopPropagation

    sender = await event.get_sender()
    target = await reply.get_sender()

    if not sender or not target or getattr(target, "bot", False):
        await event.reply(font("You cannot gift this target."))
        raise events.StopPropagation

    if int(sender.id) == int(target.id):
        await event.reply(font("You cannot gift yourself."))
        raise events.StopPropagation

    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /gift rose"))
        raise events.StopPropagation

    gift_id = item_key(parts[1])
    gift = GIFTS.get(gift_id)

    if not gift:
        await event.reply(font("Gift not found. Open /shop and check Gifts."))
        raise events.StopPropagation

    price = int(gift["price"])
    sender_wallet = await get_wallet(sender.id)

    if int(sender_wallet.get("balance", 0)) < price:
        await event.reply(font("Not enough EC."))
        raise events.StopPropagation

    await wallet_db.update_one(
        {"user_id": int(sender.id)},
        {
            "$inc": {"balance": -price},
            "$set": {"updated_at": now_ist()},
        },
        upsert=True,
    )

    await wallet_db.update_one(
        {"user_id": int(target.id)},
        {
            "$push": {
                "gifts": {
                    "from": int(sender.id),
                    "item": gift_id,
                    "name": gift["name"],
                    "at": now_ist(),
                }
            },
            "$set": {"updated_at": now_ist()},
        },
        upsert=True,
    )

    caption = (
        font(f"🎁 {user_name(sender)} gifted {gift['name']} to {user_name(target)}")
        + f"\n{font('Paid:')} {price} {CURRENCY}"
    )

    media = await get_item_media(gift_id)

    if media:
        await tbot.send_file(
            event.chat_id,
            media,
            caption=caption,
            reply_to=reply.id,
        )
    else:
        await tbot.send_message(
            event.chat_id,
            caption,
            reply_to=reply.id,
        )

    raise events.StopPropagation


if "aaa_azai_gift_alias" not in tbot.handlers_loaded:
    tbot.add_event_handler(
        gift_handler,
        events.NewMessage(pattern=r"^[/!.]gift(?: .*)?$", incoming=True),
    )
    tbot.handlers_loaded.add("aaa_azai_gift_alias")
