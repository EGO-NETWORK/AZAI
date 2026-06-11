import time
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
CURRENCY = "EC"
DAILY_REWARD = 100
CHAT_REWARD_EC = 5
CHAT_REWARD_XP = 10
CHAT_VALID_COUNT = 10
CHAT_COOLDOWN = 60
SEND_FEE_PERCENT = 3

wallet_db = database["azai_wallets"]
rep_db = database["azai_reputation"]
ref_db = database["azai_referrals"]
gate_db = database["azai_group_gate"]

activity_cache = {}


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def today_key() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d")


def level_from_xp(xp: int) -> int:
    if xp >= 900:
        return 5
    if xp >= 500:
        return 4
    if xp >= 250:
        return 3
    if xp >= 100:
        return 2
    return 1


def wallet_key(user_id: int) -> dict:
    return {"user_id": int(user_id)}


def public_name(user) -> str:
    name = getattr(user, "first_name", None) or getattr(user, "username", None) or "Unknown User"
    username = getattr(user, "username", None)
    if username:
        return f"{name} (@{username})"
    return name


async def touch_user(user):
    if not user:
        return
    await wallet_db.update_one(
        wallet_key(user.id),
        {
            "$set": {
                "name": getattr(user, "first_name", None) or getattr(user, "username", None) or "Unknown User",
                "username": getattr(user, "username", None),
                "updated_at": now_ist(),
            }
        },
        upsert=True,
    )


async def display_from_row(row: dict) -> str:
    user_id = int(row.get("user_id", 0) or 0)
    name = row.get("name") or "Unknown User"
    username = row.get("username")
    try:
        user = await tbot.get_entity(user_id)
        name = getattr(user, "first_name", None) or getattr(user, "username", None) or name
        username = getattr(user, "username", None) or username
        await wallet_db.update_one(wallet_key(user_id), {"$set": {"name": name, "username": username}}, upsert=True)
    except Exception:
        pass
    if username:
        return f"{name} (@{username})"
    return name


async def get_wallet(user_id: int) -> dict:
    user_id = int(user_id)
    data = await wallet_db.find_one(wallet_key(user_id))
    if not data:
        data = {
            "user_id": user_id,
            "balance": 0,
            "xp": 0,
            "level": 1,
            "daily_at": None,
            "messages": 0,
            "created_at": now_ist(),
        }
        await wallet_db.insert_one(data)
    return data


async def add_balance(user_id: int, amount: int, xp: int = 0):
    wallet = await get_wallet(user_id)
    new_xp = int(wallet.get("xp", 0)) + int(xp)
    await wallet_db.update_one(
        wallet_key(user_id),
        {
            "$inc": {"balance": int(amount), "xp": int(xp)},
            "$set": {"level": level_from_xp(new_xp), "updated_at": now_ist()},
        },
        upsert=True,
    )


async def set_balance(user_id: int, amount: int):
    wallet = await get_wallet(user_id)
    xp = int(wallet.get("xp", 0))
    await wallet_db.update_one(
        wallet_key(user_id),
        {"$set": {"balance": max(int(amount), 0), "level": level_from_xp(xp), "updated_at": now_ist()}},
        upsert=True,
    )


async def is_verified_in_group(chat_id: int, user_id: int) -> bool:
    data = await gate_db.find_one({"chat_id": int(chat_id), "user_id": int(user_id)})
    return bool(data and data.get("done") is True)


def wallet_text(user, wallet: dict) -> str:
    name = public_name(user)
    bal = int(wallet.get("balance", 0))
    xp = int(wallet.get("xp", 0))
    lvl = int(wallet.get("level", level_from_xp(xp)))
    return (
        font("AZAI WALLET") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("User:") + f" {name}\n"
        + font("Balance:") + f" {bal} {CURRENCY}\n"
        + font("XP:") + f" {xp}\n"
        + font("Level:") + f" {lvl}\n\n"
        + font("Powered By:") + " " + BRAND
    )


def wallet_buttons():
    return [[Button.inline(font("Leaderboard"), b"azeco_leader"), Button.inline(font("Close"), b"azeco_close")]]


async def wallet_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    wallet = await get_wallet(sender.id)
    await event.reply(wallet_text(sender, wallet), buttons=wallet_buttons())


async def daily_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    wallet = await get_wallet(sender.id)
    today = today_key()
    if wallet.get("daily_at") == today:
        await event.reply(font("Daily reward already claimed today."))
        return
    await add_balance(sender.id, DAILY_REWARD, 0)
    await wallet_db.update_one(wallet_key(sender.id), {"$set": {"daily_at": today, "updated_at": now_ist()}}, upsert=True)
    await event.reply(
        font("DAILY REWARD CLAIMED") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Reward:") + f" {DAILY_REWARD} {CURRENCY}"
    )


async def send_handler(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to a user and use /send amount."))
        return
    target = await reply.get_sender()
    sender = await event.get_sender()
    await touch_user(sender)
    await touch_user(target)
    if not target or getattr(target, "bot", False):
        await event.reply(font("You cannot send credits to this target."))
        return
    if target.id == sender.id:
        await event.reply(font("You cannot send credits to yourself."))
        return
    parts = (event.raw_text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await event.reply(font("Use: /send amount"))
        return
    amount = int(parts[1])
    if amount < 10:
        await event.reply(font("Minimum send amount is 10 EC."))
        return
    sender_wallet = await get_wallet(sender.id)
    if int(sender_wallet.get("balance", 0)) < amount:
        await event.reply(font("Not enough balance."))
        return
    fee = max(int(amount * SEND_FEE_PERCENT / 100), 1)
    receive_amount = amount - fee
    await add_balance(sender.id, -amount, 0)
    await add_balance(target.id, receive_amount, 0)
    await event.reply(
        font("CREDITS SENT") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Sent:") + f" {amount} {CURRENCY}\n"
        + font("Receiver gets:") + f" {receive_amount} {CURRENCY}\n"
        + font("Fee:") + f" {fee} {CURRENCY}"
    )


async def rep_handler(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to a user and use /rep."))
        return
    target = await reply.get_sender()
    sender = await event.get_sender()
    await touch_user(sender)
    await touch_user(target)
    if not target or getattr(target, "bot", False):
        await event.reply(font("You cannot give REP to this target."))
        return
    if target.id == sender.id:
        await event.reply(font("You cannot give REP to yourself."))
        return
    key = {"from_id": int(sender.id), "target_id": int(target.id), "date": today_key()}
    old = await rep_db.find_one(key)
    if old:
        await event.reply(font("You already gave REP today."))
        return
    await rep_db.insert_one({**key, "created_at": now_ist()})
    await wallet_db.update_one(wallet_key(target.id), {"$inc": {"rep": 1}, "$set": {"updated_at": now_ist()}}, upsert=True)
    await event.reply(font("REP added."))


async def myrep_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    wallet = await get_wallet(sender.id)
    rep = int(wallet.get("rep", 0))
    await event.reply(font("Your REP:") + f" {rep}")


async def inventory_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    wallet = await get_wallet(sender.id)
    inv = wallet.get("inventory", []) or []
    if not inv:
        await event.reply(font("Your inventory is empty."))
        return
    text = font("INVENTORY") + "\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for item in inv[:20]:
        text += f"• {item}\n"
    await event.reply(text)


async def leaderboard_text(kind: str = "balance") -> str:
    label = {"balance": "RICHEST USERS", "xp": "TOP XP", "rep": "TOP REP"}.get(kind, "LEADERBOARD")
    rows = wallet_db.find({}).sort(kind, -1).limit(10)
    text = font(label) + "\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    rank = 1
    async for row in rows:
        value = int(row.get(kind, 0))
        display = await display_from_row(row)
        text += f"{rank}. {display} - {value}\n"
        rank += 1
    if rank == 1:
        text += font("No data yet.")
    return text


def leaderboard_buttons():
    return [
        [Button.inline(font("Richest"), b"azeco_lb_balance"), Button.inline(font("XP"), b"azeco_lb_xp"), Button.inline(font("REP"), b"azeco_lb_rep")],
        [Button.inline(font("Close"), b"azeco_close")],
    ]


async def leaderboard_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    await event.reply(await leaderboard_text("balance"), buttons=leaderboard_buttons())


async def economy_callback(event):
    data = event.data.decode()
    if data == "azeco_close":
        await event.delete()
    elif data == "azeco_leader":
        await event.edit(await leaderboard_text("balance"), buttons=leaderboard_buttons())
    elif data == "azeco_lb_balance":
        await event.edit(await leaderboard_text("balance"), buttons=leaderboard_buttons())
    elif data == "azeco_lb_xp":
        await event.edit(await leaderboard_text("xp"), buttons=leaderboard_buttons())
    elif data == "azeco_lb_rep":
        await event.edit(await leaderboard_text("rep"), buttons=leaderboard_buttons())


async def chat_reward_handler(event):
    if event.is_private or (event.is_channel and not event.is_group):
        return
    text = event.raw_text or ""
    if not text or text.startswith(tuple(prefix_cmds)):
        return
    if len(text.strip()) < 4:
        return
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return
    await touch_user(sender)
    if not await is_verified_in_group(event.chat_id, sender.id):
        return
    key = (int(event.chat_id), int(sender.id))
    last = activity_cache.get(key, 0)
    now = time.time()
    if now - last < CHAT_COOLDOWN:
        return
    activity_cache[key] = now
    wallet = await get_wallet(sender.id)
    current_count = int(wallet.get("messages", 0)) + 1
    await wallet_db.update_one(wallet_key(sender.id), {"$set": {"messages": current_count, "updated_at": now_ist()}}, upsert=True)
    if current_count % CHAT_VALID_COUNT == 0:
        await add_balance(sender.id, CHAT_REWARD_EC, CHAT_REWARD_XP)


if "azai_economy" not in tbot.handlers_loaded:
    tbot.add_event_handler(wallet_handler, events.NewMessage(pattern=f"^{prefix_cmds}(wallet|balance)(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(daily_handler, events.NewMessage(pattern=f"^{prefix_cmds}daily(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(send_handler, events.NewMessage(pattern=f"^{prefix_cmds}send(?: .*)?$", incoming=True))
    tbot.add_event_handler(rep_handler, events.NewMessage(pattern=f"^{prefix_cmds}rep(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(myrep_handler, events.NewMessage(pattern=f"^{prefix_cmds}myrep(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(inventory_handler, events.NewMessage(pattern=f"^{prefix_cmds}inventory(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(leaderboard_handler, events.NewMessage(pattern=f"^{prefix_cmds}leaderboard(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(economy_callback, events.CallbackQuery(pattern=b"^azeco_"))
    tbot.add_event_handler(chat_reward_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_economy")
