from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
event_db = database["azai_events"]
bday_db = database["azai_birthdays"]
settings_db = database["azai_event_settings"]


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


def today_ddmm():
    return datetime.now(IST).strftime("%d/%m")


def valid_ddmm(value: str):
    try:
        datetime.strptime(value.strip(), "%d/%m")
        return value.strip()
    except Exception:
        return None


async def events_panel(event):
    day = today_ddmm()
    total_events = await event_db.count_documents({"chat_id": int(event.chat_id)})
    total_bdays = await bday_db.count_documents({"chat_id": int(event.chat_id)})
    text = font("AZAI EVENTS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Today:") + f" {day}\n" + font("Saved Events:") + f" {total_events}\n" + font("Saved Birthdays:") + f" {total_bdays}\n\n" + font("Use /todayevents to view today.")
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


async def eventauto(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    value = raw[1].strip().lower() if len(raw) > 1 else "status"
    if value in {"on", "off"}:
        await settings_db.update_one({"chat_id": int(event.chat_id)}, {"$set": {"chat_id": int(event.chat_id), "auto": value == "on"}}, upsert=True)
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
    tbot.handlers_loaded.add("zzzz_azai_events")
