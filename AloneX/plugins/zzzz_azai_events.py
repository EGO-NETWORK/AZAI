import asyncio
from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
event_db = database["azai_events"]
bday_db = database["azai_birthdays"]
settings_db = database["azai_event_settings"]
sent_db = database["azai_event_sent"]
wallet_db = database["azai_wallets"]

BDAY_REWARD = 500
EVENT_REWARD = 200


def owner_ids():
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            if int(value):
                ids.add(int(value))
        except Exception:
            pass
    return ids


async def is_owner(event):
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


def now_ist():
    return datetime.now(IST)


def today_ddmm():
    return now_ist().strftime("%d/%m")


def today_key():
    return now_ist().strftime("%Y-%m-%d")


def valid_ddmm(value: str):
    try:
        datetime.strptime(value.strip(), "%d/%m")
        return value.strip()
    except Exception:
        return None


async def reward_user(user_id: int, amount: int):
    try:
        await wallet_db.update_one({"user_id": int(user_id)}, {"$inc": {"balance": int(amount), "xp": 5}}, upsert=True)
    except Exception:
        pass


async def already_sent(key: str) -> bool:
    return bool(await sent_db.find_one({"key": key}))


async def mark_sent(key: str, chat_id: int, kind: str):
    await sent_db.update_one({"key": key}, {"$set": {"key": key, "chat_id": int(chat_id), "kind": kind, "sent_at": int(now_ist().timestamp())}}, upsert=True)


async def safe_pin(chat_id: int, msg):
    if not msg or int(chat_id) > 0:
        return False
    try:
        await tbot.pin_message(chat_id, msg, notify=False)
        return True
    except Exception:
        return False


async def events_panel(event):
    day = today_ddmm()
    total_events = await event_db.count_documents({"chat_id": int(event.chat_id)})
    total_bdays = await bday_db.count_documents({"chat_id": int(event.chat_id)})
    data = await settings_db.find_one({"chat_id": int(event.chat_id)}) or {}
    auto = font("On") if data.get("auto") else font("Off")
    text = font("AZAI EVENTS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Today:") + f" {day}\n" + font("Auto Wish:") + f" {auto}\n" + font("Saved Events:") + f" {total_events}\n" + font("Saved Birthdays:") + f" {total_bdays}\n\n" + font("Use /todayevents to view today.")
    await event.reply(text)
    raise events.StopPropagation


async def birthday(event):
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /birthday DD/MM"))
        raise events.StopPropagation
    day = valid_ddmm(parts[1])
    if not day:
        await event.reply(font("Invalid date. Use DD/MM."))
        raise events.StopPropagation
    sender = await event.get_sender()
    await bday_db.update_one({"chat_id": int(event.chat_id), "user_id": int(sender.id)}, {"$set": {"chat_id": int(event.chat_id), "user_id": int(sender.id), "name": getattr(sender, "first_name", "Member") or "Member", "date": day}}, upsert=True)
    await event.reply(font("Birthday saved:") + f" {day}")
    raise events.StopPropagation


async def birthdays(event):
    rows = await bday_db.find({"chat_id": int(event.chat_id)}).sort("date", 1).to_list(length=50)
    text = font("SAVED BIRTHDAYS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No birthdays saved.")
    else:
        for row in rows:
            text += f"{row.get('date')} - {row.get('name')}\n"
    await event.reply(text)
    raise events.StopPropagation


async def addevent(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2 or "|" not in raw[1]:
        await event.reply(font("Use: /addevent DD/MM | title | text"))
        raise events.StopPropagation
    parts = [x.strip() for x in raw[1].split("|")]
    if len(parts) < 3:
        await event.reply(font("Use: /addevent DD/MM | title | text"))
        raise events.StopPropagation
    day = valid_ddmm(parts[0])
    if not day:
        await event.reply(font("Invalid date. Use DD/MM."))
        raise events.StopPropagation
    title = parts[1][:80]
    body = parts[2][:500]
    await event_db.update_one({"chat_id": int(event.chat_id), "title": title}, {"$set": {"chat_id": int(event.chat_id), "date": day, "title": title, "text": body}}, upsert=True)
    await event.reply(font("Event saved:") + f" {title}")
    raise events.StopPropagation


async def delevent(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /delevent title"))
        raise events.StopPropagation
    res = await event_db.delete_one({"chat_id": int(event.chat_id), "title": parts[1].strip()})
    await event.reply(font("Event deleted." if res.deleted_count else "Event not found."))
    raise events.StopPropagation


async def todayevents(event):
    day = today_ddmm()
    evs = await event_db.find({"chat_id": int(event.chat_id), "date": day}).to_list(length=20)
    bds = await bday_db.find({"chat_id": int(event.chat_id), "date": day}).to_list(length=20)
    text = font("TODAY EVENTS") + f" - {day}\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if not evs and not bds:
        text += font("No saved event for today.")
    for row in evs:
        text += font("Event:") + f" {row.get('title')}\n{row.get('text')}\n\n"
    for row in bds:
        text += font("Birthday:") + f" {row.get('name')}\n"
    await event.reply(text)
    raise events.StopPropagation


async def send_event_wish(chat_id: int, row: dict):
    key = f"{today_key()}:event:{chat_id}:{row.get('title')}"
    if await already_sent(key):
        return
    text = font("AZAI EVENT WISH") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font(str(row.get("title", "Event"))) + "\n" + str(row.get("text", "")) + "\n\n" + font("EGO Network wishes everyone a good day.")
    msg = await tbot.send_message(chat_id, text)
    await safe_pin(chat_id, msg)
    await mark_sent(key, chat_id, "event")


async def send_birthday_wish(chat_id: int, row: dict):
    user_id = int(row.get("user_id"))
    name = row.get("name") or "Member"
    key = f"{today_key()}:birthday:{chat_id}:{user_id}"
    if await already_sent(key):
        return
    group_text = font("AZAI BIRTHDAY WISH") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Happy Birthday") + f" {name}!\n" + font("Stay blessed and keep shining with EGO Network.") + f"\n\n+{BDAY_REWARD} EC"
    msg = await tbot.send_message(chat_id, group_text)
    await safe_pin(chat_id, msg)
    try:
        dm_text = font("Happy Birthday") + f" {name}!\n\n" + font("AZAI and EGO Network wish you a happy, safe, and successful year ahead.") + f"\n\nReward: +{BDAY_REWARD} EC"
        await tbot.send_message(user_id, dm_text)
    except Exception:
        pass
    await reward_user(user_id, BDAY_REWARD)
    await mark_sent(key, chat_id, "birthday")


async def run_auto_for_chat(chat_id: int):
    day = today_ddmm()
    evs = await event_db.find({"chat_id": int(chat_id), "date": day}).to_list(length=20)
    bds = await bday_db.find({"chat_id": int(chat_id), "date": day}).to_list(length=50)
    for row in evs:
        try:
            await send_event_wish(int(chat_id), row)
            await asyncio.sleep(0.5)
        except Exception:
            pass
    for row in bds:
        try:
            await send_birthday_wish(int(chat_id), row)
            await asyncio.sleep(0.5)
        except Exception:
            pass


async def run_daily_auto():
    cursor = settings_db.find({"auto": True})
    async for row in cursor:
        try:
            await run_auto_for_chat(int(row.get("chat_id")))
            await asyncio.sleep(1)
        except Exception:
            pass


async def auto_loop():
    await asyncio.sleep(10)
    while True:
        try:
            if 8 <= now_ist().hour <= 22:
                await run_daily_auto()
        except Exception:
            pass
        await asyncio.sleep(1800)


async def eventauto(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    value = raw[1].strip().lower() if len(raw) > 1 else "status"
    if value in {"on", "off"}:
        await settings_db.update_one({"chat_id": int(event.chat_id)}, {"$set": {"chat_id": int(event.chat_id), "auto": value == "on"}}, upsert=True)
    elif value == "now":
        await run_auto_for_chat(int(event.chat_id))
    data = await settings_db.find_one({"chat_id": int(event.chat_id)}) or {}
    status = font("On") if data.get("auto") else font("Off")
    await event.reply(font("Event auto status:") + f" {status}")
    raise events.StopPropagation


if "zzzz_azai_events" not in tbot.handlers_loaded:
    tbot.add_event_handler(events_panel, events.NewMessage(pattern=f"^{prefix_cmds}events(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(birthday, events.NewMessage(pattern=f"^{prefix_cmds}birthday(?: .*)?$", incoming=True))
    tbot.add_event_handler(birthdays, events.NewMessage(pattern=f"^{prefix_cmds}birthdays$", incoming=True))
    tbot.add_event_handler(addevent, events.NewMessage(pattern=f"^{prefix_cmds}addevent(?: .*)?$", incoming=True))
    tbot.add_event_handler(delevent, events.NewMessage(pattern=f"^{prefix_cmds}delevent(?: .*)?$", incoming=True))
    tbot.add_event_handler(todayevents, events.NewMessage(pattern=f"^{prefix_cmds}todayevents$", incoming=True))
    tbot.add_event_handler(eventauto, events.NewMessage(pattern=f"^{prefix_cmds}eventauto(?: .*)?$", incoming=True))
    try:
        tbot.loop.create_task(auto_loop())
    except Exception:
        pass
    tbot.handlers_loaded.add("zzzz_azai_events")
