import random
import time
from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
CURRENCY = "EC"
wallet_db = database["azai_wallets"]
media_db = database["azai_game_media"]

MISSION_COOLDOWN = 7200
MISSION_ENTRY = 300
MISSION_SUCCESS = 35
RAID_MIN = 1000
RAID_PERCENT = 70


def ts():
    return int(time.time())


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


def uname(user):
    if not user:
        return "User"
    try:
        if int(user.id) in owner_ids():
            return "MR EGO"
    except Exception:
        pass
    name = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
    username = getattr(user, "username", None)
    return f"{name} (@{username})" if username else name


def left_time(seconds):
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


async def wallet(user_id, user=None):
    user_id = int(user_id)
    data = await wallet_db.find_one({"user_id": user_id})
    if not data:
        data = {"user_id": user_id, "balance": 0, "power": 100, "level": 1, "game": {}, "created_at": now_ist()}
        await wallet_db.insert_one(data)
    fix = {}
    if user:
        fix["name"] = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
        fix["username"] = getattr(user, "username", None)
    for key, default in (("balance", 0), ("power", 100), ("level", 1)):
        if key not in data:
            fix[key] = default
            data[key] = default
    if not isinstance(data.get("game"), dict):
        fix["game"] = {}
        data["game"] = {}
    if fix:
        await wallet_db.update_one({"user_id": user_id}, {"$set": fix}, upsert=True)
        data.update(fix)
    return data


def active_protect(data):
    return int((data.get("game", {}) or {}).get("protection_until", 0) or 0)


def cd(data, key, wait):
    last = int((data.get("game", {}) or {}).get(key, 0) or 0)
    return max(0, wait - (ts() - last))


async def media(key):
    data = await media_db.find_one({"key": key})
    if not data:
        return None
    try:
        msg = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        return msg.media if msg and msg.media else None
    except Exception:
        return None


async def send(event, key, text):
    pic = await media(key)
    if pic:
        await tbot.send_file(event.chat_id, pic, caption=text)
    else:
        await event.reply(text)
    raise events.StopPropagation


async def attack(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Attack requires a target. Reply to a user in a group."))
        raise events.StopPropagation
    attacker, target = await event.get_sender(), await reply.get_sender()
    if not attacker or not target or getattr(target, "bot", False) or int(attacker.id) == int(target.id):
        await event.reply(font("Invalid attack target."))
        raise events.StopPropagation
    aw, tw = await wallet(attacker.id, attacker), await wallet(target.id, target)
    ap, tp = int(aw.get("power", 100)), int(tw.get("power", 100))
    chance = 50 if ap == tp else (65 if ap > tp else 35)
    winner = attacker if random.randint(1, 100) <= chance else target
    loser = target if int(winner.id) == int(attacker.id) else attacker
    reward, power = random.randint(100, 300), random.randint(5, 20)
    await wallet_db.update_one({"user_id": int(winner.id)}, {"$inc": {"balance": reward, "power": power, "game.attack_wins": 1}, "$set": {"updated_at": now_ist()}}, upsert=True)
    await wallet_db.update_one({"user_id": int(loser.id)}, {"$inc": {"game.attack_losses": 1}}, upsert=True)
    text = font("ATTACK RESULT") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(attacker)} " + font("challenged") + f" {uname(target)} " + font("in a power battle.") + f"\n\n{font('Winner:')} {uname(winner)}\n{font('Reward:')} {reward} {CURRENCY}\n{font('Power:')} +{power}"
    await send(event, "attack", text)


async def raid(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Raid requires a target. Reply to a user in a group."))
        raise events.StopPropagation
    attacker, target = await event.get_sender(), await reply.get_sender()
    if not attacker or not target or getattr(target, "bot", False) or int(attacker.id) == int(target.id):
        await event.reply(font("Invalid raid target."))
        raise events.StopPropagation
    aw, tw = await wallet(attacker.id, attacker), await wallet(target.id, target)
    tb = int(tw.get("balance", 0))
    if tb < RAID_MIN:
        text = font("RAID UNAVAILABLE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(target)}" + font("'s wallet does not meet the minimum raid requirement.") + f"\n\n{font('Minimum:')} {RAID_MIN} {CURRENCY}"
        await send(event, "raid", text)
    if active_protect(tw) > ts():
        text = font("PROTECTED VAULT") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(target)} " + font("is under protection.") + f"\n\n{font('Raid Blocked')}\n{font('Loot:')} 0 {CURRENCY}"
        await send(event, "raid", text)
    ap, tp = int(aw.get("power", 100)), int(tw.get("power", 100))
    chance = 50 if ap == tp else (90 if ap > tp else 10)
    if random.randint(1, 100) <= chance:
        loot = max(1, int(tb * RAID_PERCENT / 100))
        await wallet_db.update_one({"user_id": int(target.id)}, {"$inc": {"balance": -loot, "game.raid_losses": 1}, "$set": {"updated_at": now_ist()}}, upsert=True)
        await wallet_db.update_one({"user_id": int(attacker.id)}, {"$inc": {"balance": loot, "game.raid_wins": 1}, "$set": {"updated_at": now_ist()}}, upsert=True)
        text = font("RAID SUCCESSFUL") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(attacker)} " + font("completed a vault raid on") + f" {uname(target)}.\n\n{font('Secured:')} {loot} {CURRENCY}"
    else:
        await wallet_db.update_one({"user_id": int(attacker.id)}, {"$inc": {"game.raid_failed": 1}}, upsert=True)
        text = font("VAULT SAFE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(attacker)} " + font("tried to raid") + f" {uname(target)}, " + font("but the vault stayed locked.") + f"\n\n{font('Loot:')} 0 {CURRENCY}"
    await send(event, "raid", text)


async def heist(event):
    user = await event.get_sender()
    data = await wallet(user.id, user)
    wait = cd(data, "heist_at", MISSION_COOLDOWN)
    if wait:
        await event.reply(font("Heist cooldown active.") + f"\n{font('Try again in:')} {left_time(wait)}")
        raise events.StopPropagation
    if int(data.get("balance", 0)) < MISSION_ENTRY:
        await event.reply(font("Heist requires entry fee:") + f" {MISSION_ENTRY} {CURRENCY}")
        raise events.StopPropagation
    success = random.randint(1, 100) <= MISSION_SUCCESS
    reward = random.randint(1500, 5000) if success else 0
    inc = {"balance": reward - MISSION_ENTRY, "game.heist_wins" if success else "game.heist_losses": 1}
    await wallet_db.update_one({"user_id": int(user.id)}, {"$inc": inc, "$set": {"game.heist_at": ts(), "updated_at": now_ist()}}, upsert=True)
    result = font("Success") if success else font("Failed")
    text = font("HEIST MISSION") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(user)} " + font("entered a high risk hustle mission.") + f"\n\n{font('Entry:')} {MISSION_ENTRY} {CURRENCY}\n{font('Result:')} {result}\n{font('Reward:')} {reward} {CURRENCY}"
    await send(event, "heist", text)


if "zzzz_azai_ego_hustle_actions" not in tbot.handlers_loaded:
    tbot.add_event_handler(attack, events.NewMessage(pattern=f"^{prefix_cmds}attack(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(raid, events.NewMessage(pattern=f"^{prefix_cmds}raid(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(heist, events.NewMessage(pattern=f"^{prefix_cmds}heist(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("zzzz_azai_ego_hustle_actions")
