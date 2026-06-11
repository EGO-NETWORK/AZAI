from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
CURRENCY = "EC"
wallet_db = database["azai_wallets"]

CARS = {
    "car_scorpio_s11_white": {"name": "Scorpio S11", "color": "White", "price": 5000, "rarity": "Rare"},
    "car_scorpio_s11_black": {"name": "Scorpio S11", "color": "Black", "price": 5500, "rarity": "Rare Plus"},
    "car_fortuner_black": {"name": "Toyota Fortuner", "color": "Black", "price": 7000, "rarity": "Epic"},
    "car_bmw_m5": {"name": "BMW M5", "color": "Default", "price": 8000, "rarity": "Epic Plus"},
}

BIKES = {
    "bike_splendor": {"name": "Splendor", "color": "Default", "price": 1000, "rarity": "Common"},
    "bike_duke_390": {"name": "Duke 390", "color": "Default", "price": 3000, "rarity": "Rare"},
    "bike_ninja_h2r": {"name": "Kawasaki Ninja H2R", "color": "Default", "price": 12000, "rarity": "Legendary"},
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


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


async def get_wallet(user_id: int) -> dict:
    user_id = int(user_id)
    data = await wallet_db.find_one({"user_id": user_id})
    if not data:
        data = {"user_id": user_id, "balance": 0, "xp": 0, "level": 1, "inventory": [], "created_at": now_ist()}
        await wallet_db.insert_one(data)
    return data


async def add_balance(user_id: int, amount: int):
    await get_wallet(user_id)
    await wallet_db.update_one({"user_id": int(user_id)}, {"$inc": {"balance": int(amount)}, "$set": {"updated_at": now_ist()}}, upsert=True)


def item_line(item_id: str, item: dict) -> str:
    name = item.get("name", item_id)
    color = item.get("color", "Default")
    price = int(item.get("price", 0))
    rarity = item.get("rarity", "Normal")
    return f"• {name} ({color}) - {price} {CURRENCY} [{rarity}]\n  ID: {item_id}"


def shop_home_text() -> str:
    return (
        font("MARKET") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a category below.") + "\n"
        + font("Bought vehicles go to Garage.") + "\n"
        + font("Use /inventory or /garage to see item IDs.") + "\n"
        + font("Set bike: /setbike bike_splendor") + "\n"
        + font("Set car: /setcar car_scorpio_s11_black") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def shop_buttons():
    return [
        [Button.inline(font("Cars"), b"azm_cars"), Button.inline(font("Bikes"), b"azm_bikes")],
        [Button.inline(font("Gifts"), b"azm_gifts"), Button.inline(font("Boosters"), b"azm_boosters")],
        [Button.inline(font("Garage"), b"azm_garage"), Button.inline(font("Vault"), b"azm_vault")],
        [Button.inline(font("Inventory"), b"azm_inventory"), Button.inline(font("Close"), b"azm_close")],
    ]


def back_buttons():
    return [[Button.inline(font("Back"), b"azm_home"), Button.inline(font("Close"), b"azm_close")]]


def items_buttons(items: dict, prefix: str):
    rows = []
    row = []
    for item_id, item in items.items():
        label = font(item["name"])
        row.append(Button.inline(label, f"azm_view_{item_id}".encode()))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([Button.inline(font("Back"), b"azm_home"), Button.inline(font("Close"), b"azm_close")])
    return rows


def category_text(title: str, items: dict) -> str:
    text = font(title) + "\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for item_id, item in items.items():
        text += item_line(item_id, item) + "\n"
    text += "\n" + font("Tap an item to view or buy.")
    return text


def gift_text() -> str:
    text = font("GIFTS") + "\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key, item in GIFTS.items():
        text += f"• {item['name']} - {item['price']} {CURRENCY}\n  ID: {key}\n"
    text += "\n" + font("Use: /gift item_id by replying to a user.")
    return text


def view_item_text(item_id: str, item: dict) -> str:
    return (
        font("ITEM DETAILS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Name:") + f" {item.get('name')}\n"
        + font("Color:") + f" {item.get('color', 'Default')}\n"
        + font("Rarity:") + f" {item.get('rarity', 'Normal')}\n"
        + font("Price:") + f" {item.get('price', 0)} {CURRENCY}\n\n"
        + font("Item ID:") + f" {item_id}\n\n"
        + font("After buy, use /inventory or /garage to check IDs.")
    )


def buy_buttons(item_id: str):
    return [[Button.inline(font("Buy"), f"azm_buy_{item_id}".encode())], [Button.inline(font("Back"), b"azm_home"), Button.inline(font("Close"), b"azm_close")]]


def all_market_items() -> dict:
    data = {}
    data.update(CARS)
    data.update(BIKES)
    return data


async def buy_item(event, item_id: str):
    items = all_market_items()
    item = items.get(item_id)
    if not item:
        await event.answer(font("Item not found."), alert=True)
        return
    sender = await event.get_sender()
    wallet = await get_wallet(sender.id)
    owned = wallet.get("inventory", []) or []
    if item_id in owned:
        await event.answer(font("You already own this item."), alert=True)
        return
    price = int(item["price"])
    if int(wallet.get("balance", 0)) < price:
        await event.answer(font("Not enough EC."), alert=True)
        return
    await add_balance(sender.id, -price)
    update = {"$addToSet": {"inventory": item_id}, "$set": {"updated_at": now_ist()}}
    if item_id.startswith("car_"):
        update["$addToSet"]["garage.cars"] = item_id
    if item_id.startswith("bike_"):
        update["$addToSet"]["garage.bikes"] = item_id
    await wallet_db.update_one({"user_id": int(sender.id)}, update, upsert=True)
    guide = ""
    if item_id.startswith("bike_"):
        guide = f"\n\nNext:\n/inventory\n/setbike {item_id}"
    if item_id.startswith("car_"):
        guide = f"\n\nNext:\n/inventory\n/setcar {item_id}"
    await event.edit(
        font("PURCHASE COMPLETE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Item:") + f" {item['name']}\n"
        + font("Item ID:") + f" {item_id}\n"
        + font("Paid:") + f" {price} {CURRENCY}\n"
        + font("Saved to your Garage/Inventory.") + guide,
        buttons=back_buttons(),
    )


async def shop_handler(event):
    await event.reply(shop_home_text(), buttons=shop_buttons())


async def garage_text(user_id: int) -> str:
    wallet = await get_wallet(user_id)
    garage = wallet.get("garage", {}) or {}
    cars = garage.get("cars", []) or []
    bikes = garage.get("bikes", []) or []
    active_car = garage.get("active_car")
    active_bike = garage.get("active_bike")
    text = font("GARAGE") + "\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += font("Active Car:") + f" {active_car or 'None'}\n"
    text += font("Active Bike:") + f" {active_bike or 'None'}\n\n"
    text += font("Cars:") + "\n"
    text += "\n".join([f"• {CARS.get(x, {}).get('name', x)}\n  ID: {x}\n  Use: /setcar {x}" for x in cars]) if cars else font("No cars owned yet.")
    text += "\n\n" + font("Bikes:") + "\n"
    text += "\n".join([f"• {BIKES.get(x, {}).get('name', x)}\n  ID: {x}\n  Use: /setbike {x}" for x in bikes]) if bikes else font("No bikes owned yet.")
    return text


async def garage_handler(event):
    sender = await event.get_sender()
    await event.reply(await garage_text(sender.id), buttons=back_buttons())


async def vault_handler(event):
    await event.reply(
        font("VAULT") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Rare, limited, and owner-gifted items will appear here.") + "\n"
        + font("Vault items are separate from normal market items."),
        buttons=back_buttons(),
    )


async def set_vehicle(event, kind: str):
    sender = await event.get_sender()
    parts = (event.raw_text or "").split()
    if len(parts) < 2:
        await event.reply(font("Use item ID after the command."))
        return
    item_id = parts[1].strip()
    wallet = await get_wallet(sender.id)
    garage = wallet.get("garage", {}) or {}
    owned_list = garage.get("cars" if kind == "car" else "bikes", []) or []
    if item_id not in owned_list:
        await event.reply(font("You do not own this item. Open /garage to check item IDs."))
        return
    field = "garage.active_car" if kind == "car" else "garage.active_bike"
    await wallet_db.update_one({"user_id": int(sender.id)}, {"$set": {field: item_id, "updated_at": now_ist()}}, upsert=True)
    await event.reply(font("Active vehicle updated:") + f" {item_id}")


async def setcar_handler(event):
    await set_vehicle(event, "car")


async def setbike_handler(event):
    await set_vehicle(event, "bike")


async def gift_handler(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to a user and use /gift item_id."))
        return
    sender = await event.get_sender()
    target = await reply.get_sender()
    if not target or getattr(target, "bot", False):
        await event.reply(font("You cannot gift this target."))
        return
    if target.id == sender.id:
        await event.reply(font("You cannot gift yourself."))
        return
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /gift rose"))
        return
    key = parts[1].lower().replace(" ", "_")
    item = GIFTS.get(key)
    if not item:
        await event.reply(font("Gift not found. Open /shop and check Gifts."))
        return
    wallet = await get_wallet(sender.id)
    price = int(item["price"])
    if int(wallet.get("balance", 0)) < price:
        await event.reply(font("Not enough EC."))
        return
    await add_balance(sender.id, -price)
    await wallet_db.update_one(
        {"user_id": int(target.id)},
        {"$push": {"gifts": {"from": int(sender.id), "item": key, "name": item["name"], "at": now_ist()}}, "$set": {"updated_at": now_ist()}},
        upsert=True,
    )
    await event.reply(
        font("GIFT SENT") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Gift:") + f" {item['name']}\n"
        + font("Item ID:") + f" {key}\n"
        + font("Paid:") + f" {price} {CURRENCY}"
    )


async def market_callback(event):
    data = event.data.decode()
    if data == "azm_close":
        await event.delete()
    elif data == "azm_home":
        await event.edit(shop_home_text(), buttons=shop_buttons())
    elif data == "azm_cars":
        await event.edit(category_text("CARS", CARS), buttons=items_buttons(CARS, "cars"))
    elif data == "azm_bikes":
        await event.edit(category_text("BIKES", BIKES), buttons=items_buttons(BIKES, "bikes"))
    elif data == "azm_gifts":
        await event.edit(gift_text(), buttons=back_buttons())
    elif data == "azm_boosters":
        await event.edit(font("BOOSTERS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Working boosters will be added after economy testing."), buttons=back_buttons())
    elif data == "azm_garage":
        sender = await event.get_sender()
        await event.edit(await garage_text(sender.id), buttons=back_buttons())
    elif data == "azm_vault":
        await event.edit(font("VAULT") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Rare and owner-gifted items will appear here."), buttons=back_buttons())
    elif data == "azm_inventory":
        await event.edit(font("Open /inventory or /garage to view saved item IDs."), buttons=back_buttons())
    elif data.startswith("azm_view_"):
        item_id = data.replace("azm_view_", "", 1)
        item = all_market_items().get(item_id)
        if not item:
            await event.answer(font("Item not found."), alert=True)
            return
        await event.edit(view_item_text(item_id, item), buttons=buy_buttons(item_id))
    elif data.startswith("azm_buy_"):
        item_id = data.replace("azm_buy_", "", 1)
        await buy_item(event, item_id)


if "azai_market" not in tbot.handlers_loaded:
    tbot.add_event_handler(shop_handler, events.NewMessage(pattern=f"^{prefix_cmds}shop(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(garage_handler, events.NewMessage(pattern=f"^{prefix_cmds}garage(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(vault_handler, events.NewMessage(pattern=f"^{prefix_cmds}vault(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(setcar_handler, events.NewMessage(pattern=f"^{prefix_cmds}setcar(?: .*)?$", incoming=True))
    tbot.add_event_handler(setbike_handler, events.NewMessage(pattern=f"^{prefix_cmds}setbike(?: .*)?$", incoming=True))
    tbot.add_event_handler(gift_handler, events.NewMessage(pattern=f"^{prefix_cmds}gift(?: .*)?$", incoming=True))
    tbot.add_event_handler(market_callback, events.CallbackQuery(pattern=b"^azm_"))
    tbot.handlers_loaded.add("azai_market")
