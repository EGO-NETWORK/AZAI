from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

pic_db = database["azai_item_pics"]
wallet_db = database["azai_wallets"]
CURRENCY = "EC"

CARS = {
    "car_scorpio_s11_white": {"name": "Scorpio S11", "price": 5000},
    "car_scorpio_s11_black": {"name": "Scorpio S11", "price": 5500},
    "car_fortuner_black": {"name": "Toyota Fortuner", "price": 7000},
    "car_bmw_m5": {"name": "BMW M5", "price": 8000},
}

BIKES = {
    "bike_splendor": {"name": "Splendor", "price": 1000},
    "bike_duke_390": {"name": "Duke 390", "price": 3000},
    "bike_ninja_h2r": {"name": "Kawasaki Ninja H2R", "price": 12000},
}

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
    "surprise": "surprise_box",
    "surprisebox": "surprise_box",
    "love_letter": "letter",
    "note": "letter",
    "message": "letter",
}

ITEM_IDS = set(CARS) | set(BIKES) | set(GIFTS)


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


def key_name(raw: str) -> str:
    key = (raw or "").lower().strip().replace(" ", "_").replace("-", "_")
    return ALIASES.get(key, key)


def all_items() -> dict:
    data = {}
    data.update(CARS)
    data.update(BIKES)
    data.update(GIFTS)
    return data


async def get_wallet(user_id: int) -> dict:
    data = await wallet_db.find_one({"user_id": int(user_id)})
    if not data:
        data = {"user_id": int(user_id), "balance": 0, "inventory": [], "garage": {}}
        await wallet_db.insert_one(data)
    return data


async def add_balance(user_id: int, amount: int):
    await get_wallet(user_id)
    await wallet_db.update_one({"user_id": int(user_id)}, {"$inc": {"balance": int(amount)}}, upsert=True)


async def get_saved_media(item_id: str):
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


async def send_card(event, item_id: str, caption: str, buttons=None) -> bool:
    media = await get_saved_media(item_id)
    if not media:
        return False
    await tbot.send_file(event.chat_id, media, caption=caption, buttons=buttons)
    return True


async def set_item_pic(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /setitempic item_id by replying to photo."))
        raise events.StopPropagation
    item_id = key_name(parts[1])
    if item_id not in ITEM_IDS:
        await event.reply(font("Unknown item id."))
        raise events.StopPropagation
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to item photo first."))
        raise events.StopPropagation
    await pic_db.update_one(
        {"item_id": item_id},
        {"$set": {"item_id": item_id, "chat_id": int(reply.chat_id), "msg_id": int(reply.id)}},
        upsert=True,
    )
    await event.reply(font("Item photo saved:") + f" {item_id}")
    raise events.StopPropagation


async def buy_pic_callback(event):
    data = event.data.decode()
    item_id = data.replace("azm_buy_", "", 1)
    item = all_items().get(item_id)
    if not item or item_id in GIFTS:
        return
    sender = await event.get_sender()
    wallet = await get_wallet(sender.id)
    if item_id in (wallet.get("inventory", []) or []):
        await event.answer(font("You already own this item."), alert=True)
        raise events.StopPropagation
    price = int(item["price"])
    if int(wallet.get("balance", 0)) < price:
        await event.answer(font("Not enough EC."), alert=True)
        raise events.StopPropagation
    await add_balance(sender.id, -price)
    update = {"$addToSet": {"inventory": item_id}}
    if item_id.startswith("car_"):
        update["$addToSet"]["garage.cars"] = item_id
    if item_id.startswith("bike_"):
        update["$addToSet"]["garage.bikes"] = item_id
    await wallet_db.update_one({"user_id": int(sender.id)}, update, upsert=True)
    caption = font("PURCHASE COMPLETE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Item:") + f" {item['name']}\n" + font("Paid:") + f" {price} {CURRENCY}\n\n" + font("Saved to Garage/Inventory.")
    sent = await send_card(event, item_id, caption, buttons=[[Button.inline(font("Back"), b"azm_home"), Button.inline(font("Close"), b"azm_close")]])
    if sent:
        await event.delete()
    else:
        await event.edit(caption, buttons=[[Button.inline(font("Back"), b"azm_home"), Button.inline(font("Close"), b"azm_close")]])
    raise events.StopPropagation


async def garage_pic_handler(event):
    sender = await event.get_sender()
    wallet = await get_wallet(sender.id)
    garage = wallet.get("garage", {}) or {}
    active = garage.get("active_car") or garage.get("active_bike")
    cars = garage.get("cars", []) or []
    bikes = garage.get("bikes", []) or []
    text = font("GARAGE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += font("Active Car:") + f" {garage.get('active_car') or 'None'}\n"
    text += font("Active Bike:") + f" {garage.get('active_bike') or 'None'}\n\n"
    text += font("Cars:") + "\n" + ("\n".join([f"• {CARS.get(x, {}).get('name', x)}" for x in cars]) if cars else font("No cars owned yet."))
    text += "\n\n" + font("Bikes:") + "\n" + ("\n".join([f"• {BIKES.get(x, {}).get('name', x)}" for x in bikes]) if bikes else font("No bikes owned yet."))
    if active and await send_card(event, active, text):
        pass
    else:
        await event.reply(text)
    raise events.StopPropagation


async def gift_pic_handler(event):
    reply = await event.get_reply_message()
    if not reply:
        return
    sender = await event.get_sender()
    target = await reply.get_sender()
    if not target or getattr(target, "bot", False) or int(target.id) == int(sender.id):
        return
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        return
    item_id = key_name(parts[1])
    item = GIFTS.get(item_id)
    if not item:
        return
    wallet = await get_wallet(sender.id)
    price = int(item["price"])
    if int(wallet.get("balance", 0)) < price:
        await event.reply(font("Not enough EC."))
        raise events.StopPropagation
    await add_balance(sender.id, -price)
    await wallet_db.update_one({"user_id": int(target.id)}, {"$push": {"gifts": {"from": int(sender.id), "item": item_id, "name": item["name"]}}}, upsert=True)
    text = font("GIFT SENT") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Gift:") + f" {item['name']}\n" + font("Paid:") + f" {price} {CURRENCY}"
    if not await send_card(event, item_id, text):
        await event.reply(text)
    raise events.StopPropagation


if "aaa_azai_item_pics" not in tbot.handlers_loaded:
    tbot.add_event_handler(set_item_pic, events.NewMessage(pattern=f"^{prefix_cmds}setitempic(?: .*)?$", incoming=True))
    tbot.add_event_handler(garage_pic_handler, events.NewMessage(pattern=f"^{prefix_cmds}garage(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(gift_pic_handler, events.NewMessage(pattern=f"^{prefix_cmds}gift(?: .*)?$", incoming=True))
    tbot.add_event_handler(buy_pic_callback, events.CallbackQuery(pattern=b"^azm_buy_"))
    tbot.handlers_loaded.add("aaa_azai_item_pics")
