import random
import time
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
CURRENCY = "EC"
BRAND = font("EGO Network - EST. 2026")
wallet_db = database["azai_wallets"]
media_db = database["azai_game_media"]

DAILY_REWARD = 500
WORK_COOLDOWN = 600
LUCK_COOLDOWN = 14400
PROTECT = {"6h": (21600, 200), "1d": (86400, 500)}
WORKS = ["completed a delivery shift", "completed an EGO market task", "finished a garage task", "closed a client task", "completed an online work task", "handled a support task"]
MEDIA_COMMANDS = {"setgamepic": "game", "setworkpic": "work", "setluckpic": "luck", "setleaderboardpic": "leaderboard", "setgameprofilepic": "profile"}


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


async def is_owner(event):
    user = await event.get_sender()
    return bool(user and int(user.id) in owner_ids())


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


def protect_text(data):
    until = active_protect(data)
    if until > ts():
        return font("Active") + f" ({left_time(until - ts())})"
    return font("Inactive")


def cd(data, key, wait):
    last = int((data.get("game", {}) or {}).get(key, 0) or 0)
    return max(0, wait - (ts() - last))


def buttons():
    return [
        [Button.inline(font("Wallet"), b"egoh_bal"), Button.inline(font("Daily"), b"egoh_daily")],
        [Button.inline(font("Work"), b"egoh_work"), Button.inline(font("Luck"), b"egoh_luck")],
        [Button.inline(font("Raid Help"), b"egoh_raid_help"), Button.inline(font("Heist"), b"egoh_heist")],
        [Button.inline(font("Profile"), b"egoh_profile"), Button.inline(font("Leaderboard"), b"egoh_top")],
        [Button.inline(font("Close"), b"egoh_close")],
    ]


def back():
    return [[Button.inline(font("EGO Hustle"), b"egoh_home"), Button.inline(font("Close"), b"egoh_close")]]


def home_text():
    return (
        "EGO HUSTLE COMMAND GUIDE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "EGO Network - EST. 2026\n\n"
        "OPEN PANEL: /hustle /game /egohustle\n\n"
        "/bal - Check your EC wallet.\n"
        "/daily - Claim daily EC reward.\n"
        "/work - Earn EC by work mode.\n"
        "/luck - Try luck rewards.\n"
        "/protect - Activate wallet protection.\n"
        "/raid - Raid another user's wallet. Reply to target.\n"
        "/attack - Attack another user. Reply to target.\n"
        "/heist - High risk EC heist.\n"
        "/profile - Check your player profile.\n"
        "/leaderboard - Top EC players.\n"
    )


async def media(key):
    data = await media_db.find_one({"key": key})
    if not data:
        return None
    try:
        msg = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        return msg.media if msg and msg.media else None
    except Exception:
        return None


async def send(event, key, text, btn=None):
    pic = await media(key)
    if pic:
        await tbot.send_file(event.chat_id, pic, caption=text, buttons=btn)
    else:
        await event.reply(text, buttons=btn)
    raise events.StopPropagation


async def save_media(event, key):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to media first."))
        raise events.StopPropagation
    await media_db.update_one({"key": key}, {"$set": {"key": key, "chat_id": int(reply.chat_id), "msg_id": int(reply.id), "updated_at": now_ist()}}, upsert=True)
    await event.reply(font("EGO Hustle media saved:") + f" {key}")
    raise events.StopPropagation


async def hustle(event):
    await send(event, "game", home_text(), buttons())


async def bal_text(user, data):
    return font("EGO WALLET") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + font("Name:") + f" {uname(user)}\n" + font("Balance:") + f" {int(data.get('balance', 0))} {CURRENCY}\n" + font("Power:") + f" {int(data.get('power', 100))}\n" + font("Level:") + f" {int(data.get('level', 1))}\n" + font("Protection:") + f" {protect_text(data)}"


async def bal(event):
    reply = await event.get_reply_message()
    user = await reply.get_sender() if reply else await event.get_sender()
    data = await wallet(user.id, user)
    await event.reply(await bal_text(user, data), buttons=back())
    raise events.StopPropagation


async def daily_result(user):
    data = await wallet(user.id, user)
    wait = cd(data, "daily_at", 86400)
    if wait:
        return font("Daily reward already claimed.") + f"\n{font('Try again in:')} {left_time(wait)}"
    await wallet_db.update_one({"user_id": int(user.id)}, {"$inc": {"balance": DAILY_REWARD}, "$set": {"game.daily_at": ts(), "updated_at": now_ist()}}, upsert=True)
    return font("DAILY REWARD") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(user)} " + font("claimed the daily hustle reward.") + f"\n\n{font('Reward:')} {DAILY_REWARD} {CURRENCY}"


async def daily(event):
    await event.reply(await daily_result(await event.get_sender()), buttons=back())
    raise events.StopPropagation


async def work_result(user):
    data = await wallet(user.id, user)
    wait = cd(data, "work_at", WORK_COOLDOWN)
    if wait:
        return font("Work cooldown active.") + f"\n{font('Try again in:')} {left_time(wait)}"
    rare = random.randint(1, 100) <= 12
    amount = random.randint(800, 1200) if rare else random.randint(200, 700)
    task = random.choice(WORKS)
    await wallet_db.update_one({"user_id": int(user.id)}, {"$inc": {"balance": amount}, "$set": {"game.work_at": ts(), "updated_at": now_ist()}}, upsert=True)
    return font("WORK COMPLETE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(user)} {font(task)}.\n\n{font('Earned:')} {amount} {CURRENCY}"


async def work(event):
    await send(event, "work", await work_result(await event.get_sender()), back())


async def protect(event):
    user = await event.get_sender()
    parts = (event.raw_text or "").split(maxsplit=1)
    plan = parts[1].strip().lower() if len(parts) > 1 else ""
    if plan not in PROTECT:
        await event.reply(font("VAULT PROTECTION") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n/protect 6h - 200 EC\n/protect 1d - 500 EC")
        raise events.StopPropagation
    seconds, price = PROTECT[plan]
    data = await wallet(user.id, user)
    if int(data.get("balance", 0)) < price:
        await event.reply(font("Not enough EC."))
        raise events.StopPropagation
    await wallet_db.update_one({"user_id": int(user.id)}, {"$inc": {"balance": -price}, "$set": {"game.protection_until": ts() + seconds, "updated_at": now_ist()}}, upsert=True)
    text = font("VAULT PROTECTION") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(user)} " + font("activated vault protection.") + f"\n\n{font('Duration:')} {plan}\n{font('Paid:')} {price} {CURRENCY}"
    await send(event, "game", text, back())


async def luck_result(user):
    data = await wallet(user.id, user)
    wait = cd(data, "luck_at", LUCK_COOLDOWN)
    if wait:
        return font("Luck cooldown active.") + f"\n{font('Try again in:')} {left_time(wait)}"
    roll = random.randint(1, 100)
    result, reward, inc, setv, extra = font("Nothing"), 0, {}, {"game.luck_at": ts(), "updated_at": now_ist()}, ""
    if roll <= 35:
        reward, result = random.randint(200, 500), font("Small Win")
        inc["balance"] = reward
    elif roll <= 60:
        reward, result = random.randint(600, 1000), font("Good Win")
        inc["balance"] = reward
    elif roll <= 75:
        reward, result = random.randint(1200, 2000), font("Big Win")
        inc["balance"] = reward
    elif roll <= 80:
        reward, result = 3000, font("Jackpot")
        inc["balance"] = reward
    elif roll <= 90:
        result = font("Shield Bonus")
        setv["game.protection_until"] = ts() + 43200
        extra = "\n" + font("Protection:") + " 12h"
    elif roll <= 97:
        result = font("Power Boost")
        inc["power"] = 20
        extra = "\n" + font("Power:") + " +20"
    upd = {"$set": setv}
    if inc:
        upd["$inc"] = inc
    await wallet_db.update_one({"user_id": int(user.id)}, upd, upsert=True)
    return font("LUCK ROLL") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{uname(user)} " + font("tried their luck.") + f"\n\n{font('Result:')} {result}\n{font('Reward:')} {reward} {CURRENCY}" + extra


async def luck(event):
    await send(event, "luck", await luck_result(await event.get_sender()), back())


async def top_text():
    rows = await wallet_db.find({}).sort("balance", -1).limit(10).to_list(length=10)
    text = font("EGO HUSTLE LEADERBOARD") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if not rows:
        return text + "\n" + font("No players yet.")
    for i, row in enumerate(rows, 1):
        name = row.get("name") or row.get("username") or f"User {row.get('user_id')}"
        text += f"\n{i}. {name} - {int(row.get('balance', 0))} {CURRENCY}"
    return text


async def top(event):
    await event.reply(await top_text(), buttons=back())
    raise events.StopPropagation


async def profile_text(user, data):
    game = data.get("game", {}) or {}
    return font("EGO HUSTLE PROFILE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + font("Name:") + f" {uname(user)}\n" + font("Balance:") + f" {int(data.get('balance', 0))} {CURRENCY}\n" + font("Power:") + f" {int(data.get('power', 100))}\n" + font("Level:") + f" {int(data.get('level', 1))}\n" + font("Protection:") + f" {protect_text(data)}\n\n" + font("Raid Wins:") + f" {int(game.get('raid_wins', 0) or 0)}\n" + font("Attack Wins:") + f" {int(game.get('attack_wins', 0) or 0)}\n" + font("Heist Wins:") + f" {int(game.get('heist_wins', 0) or 0)}\n\n" + BRAND


async def profile(event):
    reply = await event.get_reply_message()
    user = await reply.get_sender() if reply else await event.get_sender()
    data = await wallet(user.id, user)
    await event.reply(await profile_text(user, data), buttons=back())
    raise events.StopPropagation


async def cb(event):
    data = event.data.decode()
    user = await event.get_sender()
    if data == "egoh_close":
        await event.delete()
    elif data == "egoh_home":
        await event.edit(home_text(), buttons=buttons())
    elif data == "egoh_bal":
        await event.edit(await bal_text(user, await wallet(user.id, user)), buttons=back())
    elif data == "egoh_daily":
        await event.edit(await daily_result(user), buttons=back())
    elif data == "egoh_work":
        await event.edit(await work_result(user), buttons=back())
    elif data == "egoh_luck":
        await event.edit(await luck_result(user), buttons=back())
    elif data == "egoh_profile":
        await event.edit(await profile_text(user, await wallet(user.id, user)), buttons=back())
    elif data == "egoh_top":
        await event.edit(await top_text(), buttons=back())
    raise events.StopPropagation


async def media_cmd(event):
    cmd = (event.raw_text or "").split()[0].lstrip("/!.").lower()
    key = MEDIA_COMMANDS.get(cmd)
    if key:
        await save_media(event, key)


if "zzzz_azai_ego_hustle_core" not in tbot.handlers_loaded:
    tbot.add_event_handler(hustle, events.NewMessage(pattern=f"^{prefix_cmds}(hustle|game|egohustle)(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(bal, events.NewMessage(pattern=f"^{prefix_cmds}(bal|wallet|balance)(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(daily, events.NewMessage(pattern=f"^{prefix_cmds}daily(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(work, events.NewMessage(pattern=f"^{prefix_cmds}work(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(protect, events.NewMessage(pattern=f"^{prefix_cmds}protect(?:@\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(luck, events.NewMessage(pattern=f"^{prefix_cmds}luck(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(top, events.NewMessage(pattern=f"^{prefix_cmds}(leaderboard|top)(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(profile, events.NewMessage(pattern=f"^{prefix_cmds}profile(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(media_cmd, events.NewMessage(pattern=f"^{prefix_cmds}(setgamepic|setworkpic|setluckpic|setleaderboardpic|setgameprofilepic)$", incoming=True))
    tbot.add_event_handler(cb, events.CallbackQuery(pattern=b"^egoh_"))
    tbot.handlers_loaded.add("zzzz_azai_ego_hustle_core")
