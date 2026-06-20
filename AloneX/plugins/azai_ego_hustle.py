import random
import time
from datetime import datetime, timedelta

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
CURRENCY = "EC"

wallet_db = database["azai_wallets"]
cooldown_db = database["azai_hustle_cooldowns"]

WORK_COOLDOWN = 10 * 60
LUCK_COOLDOWN = 4 * 60 * 60
HEIST_COOLDOWN = 2 * 60 * 60
HEIST_ENTRY = 300
RAID_MIN_TARGET_BALANCE = 1000
RAID_MAX_LOOT = 800
DEFAULT_POWER = 100


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def now_ts() -> int:
    return int(time.time())


def wallet_key(user_id: int) -> dict:
    return {"user_id": int(user_id)}


def user_name(user) -> str:
    return getattr(user, "first_name", None) or getattr(user, "username", None) or "User"


def wait_text(seconds: int) -> str:
    seconds = max(int(seconds), 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def title(text: str) -> str:
    return font(text) + "\n━━━━━━━━━━━━━━━━━━━━\n\n"


def hustle_footer() -> str:
    return "\n\n" + font("EGO HUSTLE") + " · " + BRAND


def caption(header: str, body: str) -> str:
    return title(header) + body + hustle_footer()


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
            },
            "$setOnInsert": {
                "user_id": int(user.id),
                "balance": 0,
                "xp": 0,
                "level": 1,
                "messages": 0,
                "daily_at": None,
                "power": DEFAULT_POWER,
                "created_at": now_ist(),
            },
        },
        upsert=True,
    )


async def get_wallet(user_id: int) -> dict:
    user_id = int(user_id)
    row = await wallet_db.find_one(wallet_key(user_id))
    if not row:
        row = {
            "user_id": user_id,
            "balance": 0,
            "xp": 0,
            "level": 1,
            "messages": 0,
            "daily_at": None,
            "power": DEFAULT_POWER,
            "created_at": now_ist(),
        }
        await wallet_db.insert_one(row)
    if row.get("power") is None:
        row["power"] = DEFAULT_POWER
        await wallet_db.update_one(wallet_key(user_id), {"$set": {"power": DEFAULT_POWER}}, upsert=True)
    return row


async def add_balance(user_id: int, amount: int):
    await get_wallet(user_id)
    await wallet_db.update_one(wallet_key(user_id), {"$inc": {"balance": int(amount)}, "$set": {"updated_at": now_ist()}}, upsert=True)


async def add_power(user_id: int, amount: int):
    wallet = await get_wallet(user_id)
    current = int(wallet.get("power", DEFAULT_POWER) or DEFAULT_POWER)
    await wallet_db.update_one(wallet_key(user_id), {"$set": {"power": current + int(amount), "updated_at": now_ist()}}, upsert=True)


async def set_protection(user_id: int, seconds: int):
    until = now_ts() + int(seconds)
    await get_wallet(user_id)
    await wallet_db.update_one(wallet_key(user_id), {"$set": {"protection_until": until, "protection": True, "updated_at": now_ist()}}, upsert=True)
    return until


async def protection_left(user_id: int) -> int:
    wallet = await get_wallet(user_id)
    until = int(wallet.get("protection_until") or 0)
    left = max(until - now_ts(), 0)
    if left <= 0 and wallet.get("protection"):
        await wallet_db.update_one(wallet_key(user_id), {"$set": {"protection": False}, "$unset": {"protection_until": ""}}, upsert=True)
    return left


async def cooldown_left(user_id: int, command: str, seconds: int) -> int:
    row = await cooldown_db.find_one({"user_id": int(user_id), "command": command}) or {}
    last = int(row.get("last_at") or 0)
    return max((last + int(seconds)) - now_ts(), 0)


async def set_cooldown(user_id: int, command: str):
    await cooldown_db.update_one(
        {"user_id": int(user_id), "command": command},
        {"$set": {"user_id": int(user_id), "command": command, "last_at": now_ts(), "updated_at": now_ist()}},
        upsert=True,
    )


async def hustle_handler(event):
    text = (
        font("EGO HUSTLE COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/work - " + font("earn EC by completing tasks") + "\n"
        + "/raid - " + font("reply to target and try to loot EC") + "\n"
        + "/protect 1d - " + font("activate raid shield") + "\n"
        + "/luck - " + font("claim a random bonus") + "\n"
        + "/heist - " + font("high-risk mission for EC") + "\n"
        + "/bal - " + font("check wallet") + "\n\n"
        + font("Currency:") + " EC"
    )
    await event.reply(text)


async def work_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    left = await cooldown_left(sender.id, "work", WORK_COOLDOWN)
    if left:
        await event.reply(caption("💼 Work Cooldown", font("Try again in:") + f" {wait_text(left)}"))
        return
    rare = random.randint(1, 100) <= 12
    earned = random.randint(800, 1200) if rare else random.randint(200, 700)
    await add_balance(sender.id, earned)
    await set_cooldown(sender.id, "work")
    body = font("Earned:") + f" {earned} {CURRENCY}\n" + font("Type:") + f" {'Rare Task' if rare else 'Task'}\n" + font("Cooldown:") + " 10m"
    await event.reply(caption("💼 Work Mode", body))


async def protect_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    parts = (event.raw_text or "").split()
    if len(parts) < 2 or parts[1].lower() not in {"1d", "2d", "3d"}:
        await event.reply(caption("🛡 Protect", font("Use:") + " /protect 1d / 2d / 3d"))
        return
    days = int(parts[1][0])
    await set_protection(sender.id, days * 86400)
    body = font("Shield:") + f" {days}d\n" + font("Status:") + " Active\n" + font("Raid Protection:") + " ON"
    await event.reply(caption("🛡 Protection Active", body))


async def luck_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    left = await cooldown_left(sender.id, "luck", LUCK_COOLDOWN)
    if left:
        await event.reply(caption("🍀 Luck Cooldown", font("Try again in:") + f" {wait_text(left)}"))
        return
    roll = random.randint(1, 100)
    body = ""
    if roll <= 28:
        amount = random.randint(200, 500)
        await add_balance(sender.id, amount)
        body = font("Reward:") + f" {amount} {CURRENCY}\n" + font("Type:") + " Small Luck"
    elif roll <= 52:
        amount = random.randint(600, 1000)
        await add_balance(sender.id, amount)
        body = font("Reward:") + f" {amount} {CURRENCY}\n" + font("Type:") + " Good Luck"
    elif roll <= 70:
        amount = random.randint(1200, 2000)
        await add_balance(sender.id, amount)
        body = font("Reward:") + f" {amount} {CURRENCY}\n" + font("Type:") + " Big Luck"
    elif roll <= 76:
        amount = 3000
        await add_balance(sender.id, amount)
        body = font("Reward:") + f" {amount} {CURRENCY}\n" + font("Type:") + " Jackpot"
    elif roll <= 86:
        await set_protection(sender.id, 12 * 3600)
        body = font("Reward:") + " 12h Shield\n" + font("Type:") + " Protection"
    elif roll <= 94:
        await add_power(sender.id, 20)
        body = font("Reward:") + " +20 Power\n" + font("Type:") + " Power Boost"
    else:
        body = font("Reward:") + " 0 EC\n" + font("Type:") + " Nothing"
    await set_cooldown(sender.id, "luck")
    await event.reply(caption("🍀 Luck Mode", body + "\n" + font("Cooldown:") + " 4h"))


async def raid_handler(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(caption("💀 Raid", font("Reply to a target user and use:") + " /raid"))
        return
    attacker = await event.get_sender()
    target = await reply.get_sender()
    await touch_user(attacker)
    await touch_user(target)
    if not target or getattr(target, "bot", False) or target.id == attacker.id:
        await event.reply(caption("💀 Raid Failed", font("Invalid target.")))
        return
    target_wallet = await get_wallet(target.id)
    attacker_wallet = await get_wallet(attacker.id)
    target_balance = int(target_wallet.get("balance", 0) or 0)
    if target_balance < RAID_MIN_TARGET_BALANCE:
        await event.reply(caption("💀 Raid Failed", font("Target needs at least:") + f" {RAID_MIN_TARGET_BALANCE} {CURRENCY}"))
        return
    shield = await protection_left(target.id)
    if shield > 0:
        await event.reply(caption("🛡 Target Protected", f"{user_name(target)} " + font("has shield for") + f" {wait_text(shield)}"))
        return
    attacker_power = int(attacker_wallet.get("power", DEFAULT_POWER) or DEFAULT_POWER)
    target_power = int(target_wallet.get("power", DEFAULT_POWER) or DEFAULT_POWER)
    chance = 50
    if attacker_power > target_power:
        chance = 90
    elif attacker_power < target_power:
        chance = 10
    success = random.randint(1, 100) <= chance
    if not success:
        await event.reply(caption("💀 Raid Failed", font("Target escaped. Better power, better odds.")))
        return
    loot = min(int(target_balance * 0.70), RAID_MAX_LOOT)
    loot = max(loot, 1)
    await add_balance(attacker.id, loot)
    await add_balance(target.id, -loot)
    await wallet_db.update_one(wallet_key(attacker.id), {"$inc": {"raid_wins": 1}, "$set": {"updated_at": now_ist()}}, upsert=True)
    body = font("Loot:") + f" {loot} {CURRENCY}\n" + font("Target:") + f" {user_name(target)}\n" + font("Chance:") + f" {chance}%"
    await event.reply(caption("💀 Raid Success", body))


async def heist_handler(event):
    sender = await event.get_sender()
    await touch_user(sender)
    left = await cooldown_left(sender.id, "heist", HEIST_COOLDOWN)
    if left:
        await event.reply(caption("💀 Heist Cooldown", font("Try again in:") + f" {wait_text(left)}"))
        return
    wallet = await get_wallet(sender.id)
    if int(wallet.get("balance", 0) or 0) < HEIST_ENTRY:
        await event.reply(caption("💀 Heist Blocked", font("Entry required:") + f" {HEIST_ENTRY} {CURRENCY}"))
        return
    await add_balance(sender.id, -HEIST_ENTRY)
    success = random.randint(1, 100) <= 45
    await set_cooldown(sender.id, "heist")
    if not success:
        await event.reply(caption("💀 Heist Failed", font("Entry lost:") + f" {HEIST_ENTRY} {CURRENCY}\n" + font("Cooldown:") + " 2h"))
        return
    reward = random.randint(1500, 5000)
    await add_balance(sender.id, reward)
    await wallet_db.update_one(wallet_key(sender.id), {"$inc": {"heist_wins": 1}, "$set": {"updated_at": now_ist()}}, upsert=True)
    body = font("Reward:") + f" {reward} {CURRENCY}\n" + font("Entry:") + f" {HEIST_ENTRY} {CURRENCY}\n" + font("Cooldown:") + " 2h"
    await event.reply(caption("💀 Heist Success", body))


if "azai_ego_hustle" not in tbot.handlers_loaded:
    tbot.add_event_handler(hustle_handler, events.NewMessage(pattern=f"^{prefix_cmds}hustle(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(work_handler, events.NewMessage(pattern=f"^{prefix_cmds}work(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(raid_handler, events.NewMessage(pattern=f"^{prefix_cmds}raid(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(protect_handler, events.NewMessage(pattern=f"^{prefix_cmds}protect(?: .*)?$", incoming=True))
    tbot.add_event_handler(luck_handler, events.NewMessage(pattern=f"^{prefix_cmds}luck(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(heist_handler, events.NewMessage(pattern=f"^{prefix_cmds}heist(?:@\w+)?$", incoming=True))
    tbot.handlers_loaded.add("azai_ego_hustle")
