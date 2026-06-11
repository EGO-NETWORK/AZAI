from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

store_db = database["azai_vault_items"]
wallet_db = database["azai_wallets"]
CURRENCY = "EC"


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


def key(raw):
    return (raw or "").lower().strip().replace(" ", "_").replace("-", "_")


async def wallet(user_id):
    data = await wallet_db.find_one({"user_id": int(user_id)})
    if not data:
        data = {"user_id": int(user_id), "balance": 0, "vault_items": []}
        await wallet_db.insert_one(data)
    return data


async def addvaultitem(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /addvaultitem id | name | price | stock"))
        return
    parts = [x.strip() for x in raw[1].split("|")]
    if len(parts) != 4 or not parts[2].isdigit() or not parts[3].isdigit():
        await event.reply(font("Use: /addvaultitem id | name | price | stock"))
        return
    item_id = key(parts[0])
    name = parts[1][:80]
    price = int(parts[2])
    stock = int(parts[3])
    if price < 1 or stock < 1:
        await event.reply(font("Price and stock must be above 0."))
        return
    await store_db.update_one({"item_id": item_id}, {"$set": {"item_id": item_id, "name": name, "price": price, "stock": stock}}, upsert=True)
    await event.reply(font("Vault item saved:") + f" {name}\nID: {item_id}\nPrice: {price} {CURRENCY}\nStock: {stock}")


async def vaultitems(event):
    rows = await store_db.find({"stock": {"$gt": 0}}).sort("price", 1).to_list(length=50)
    text = font("VAULT ITEMS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No vault items available.")
    else:
        for row in rows:
            text += f"• {row.get('name')}\nID: {row.get('item_id')}\nPrice: {row.get('price')} {CURRENCY}\nStock: {row.get('stock')}\n\n"
        text += font("Use /buyvault item_id")
    await event.reply(text)


async def buyvault(event):
    sender = await event.get_sender()
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /buyvault item_id"))
        return
    item_id = key(raw[1])
    item = await store_db.find_one({"item_id": item_id})
    if not item or int(item.get("stock", 0)) <= 0:
        await event.reply(font("Item not available."))
        return
    data = await wallet(sender.id)
    owned = data.get("vault_items", []) or []
    if item_id in owned:
        await event.reply(font("You already own this item."))
        return
    price = int(item.get("price", 0))
    if int(data.get("balance", 0)) < price:
        await event.reply(font("Not enough EC."))
        return
    await wallet_db.update_one({"user_id": int(sender.id)}, {"$inc": {"balance": -price}, "$addToSet": {"vault_items": item_id}}, upsert=True)
    await store_db.update_one({"item_id": item_id}, {"$inc": {"stock": -1}}, upsert=True)
    await event.reply(font("Vault item claimed.") + f"\n{item.get('name')}\nID: {item_id}\nPaid: {price} {CURRENCY}")


async def myvault(event):
    sender = await event.get_sender()
    data = await wallet(sender.id)
    items = data.get("vault_items", []) or []
    text = font("MY VAULT ITEMS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not items:
        text += font("No vault items owned yet.")
    else:
        for item_id in items[:50]:
            item = await store_db.find_one({"item_id": item_id})
            text += f"• {(item or {}).get('name', item_id)}\nID: {item_id}\n"
    await event.reply(text)


if "azai_vault_items" not in tbot.handlers_loaded:
    tbot.add_event_handler(addvaultitem, events.NewMessage(pattern=f"^{prefix_cmds}addvaultitem(?: .*)?$", incoming=True))
    tbot.add_event_handler(vaultitems, events.NewMessage(pattern=f"^{prefix_cmds}vaultitems(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(buyvault, events.NewMessage(pattern=f"^{prefix_cmds}buyvault(?: .*)?$", incoming=True))
    tbot.add_event_handler(myvault, events.NewMessage(pattern=f"^{prefix_cmds}myvault(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("azai_vault_items")
