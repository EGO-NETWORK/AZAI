import asyncio
from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
record_db = database["azai_" + "birthdays"]
chat_db = database["azai_broadcast_chats"]
log_db = database["azai_auto_event_logs"]
setting_db = database["azai_auto_event_settings"]


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


async def enabled():
    data = await setting_db.find_one({"key": "main"})
    if not data:
        return True
    return bool(data.get("enabled", True))


async def set_enabled(value: bool):
    await setting_db.update_one({"key": "main"}, {"$set": {"key": "main", "enabled": bool(value)}}, upsert=True)


def today_key(now):
    return now.strftime("%Y-%m-%d")


def group_text(rows, date_text):
    lines = [font("AZAI TODAY SPECIAL"), "━━━━━━━━━━━━━━━━━━━━━━━━━━━━", font("Date:") + f" {date_text}", ""]
    lines.append(font("Saved date wishes"))
    for index, row in enumerate(rows, 1):
        lines.append(f"{index}. {row.get('name', 'User')}")
    lines.append("")
    lines.append(font("Wishing happiness, health, respect, and clean positive energy."))
    lines.append(font("Powered By:") + " " + font("EGO Network"))
    return "\n".join(lines)


def dm_text(name, date_text):
    return (
        font("AZAI SPECIAL WISH") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Dear") + f" {name},\n"
        + font("Today your saved special date is marked in AZAI.") + "\n"
        + font("Wishing you happiness, health, respect, and a bright day.") + "\n\n"
        + font("Date:") + f" {date_text}\n"
        + font("Powered By:") + " " + font("EGO Network")
    )


async def send_group(chat_id, text):
    try:
        msg = await tbot.send_message(int(chat_id), text)
        try:
            await tbot.pin_message(int(chat_id), msg.id, notify=True)
        except Exception:
            pass
        return True
    except Exception:
        return False


async def run_once():
    if not await enabled():
        return
    now = datetime.now(IST)
    date_key = today_key(now)
    old = await log_db.find_one({"date": date_key})
    if old:
        return
    rows = await record_db.find({"day": now.day, "month": now.month}).to_list(length=200)
    if not rows:
        await log_db.update_one({"date": date_key}, {"$set": {"date": date_key, "count": 0}}, upsert=True)
        return
    date_text = f"{now.day:02d}/{now.month:02d}"
    text = group_text(rows, date_text)
    chats = await chat_db.find({"type": "group"}).to_list(length=5000)
    sent = 0
    failed = 0
    for row in chats:
        if await send_group(row.get("chat_id"), text):
            sent += 1
        else:
            failed += 1
    for row in rows:
        try:
            await tbot.send_message(int(row.get("user_id")), dm_text(row.get("name", "User"), date_text))
        except Exception:
            pass
    await log_db.update_one(
        {"date": date_key},
        {"$set": {"date": date_key, "count": len(rows), "groups_sent": sent, "groups_failed": failed}},
        upsert=True,
    )


async def loop_runner():
    await asyncio.sleep(20)
    while True:
        try:
            await run_once()
        except Exception:
            pass
        await asyncio.sleep(1800)


async def auto_event_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    mode = raw[1].strip().lower() if len(raw) > 1 else "status"
    if mode == "on":
        await set_enabled(True)
        await event.reply(font("Auto special-date wishes enabled."))
    elif mode == "off":
        await set_enabled(False)
        await event.reply(font("Auto special-date wishes disabled."))
    else:
        state = font("ON") if await enabled() else font("OFF")
        await event.reply(font("Auto special-date wishes:") + f" {state}\n" + font("Use:") + " /eventauto on | off | status")
    raise events.StopPropagation


if "azai_auto_events" not in tbot.handlers_loaded:
    try:
        tbot.loop.create_task(loop_runner())
    except Exception:
        pass
    tbot.add_event_handler(auto_event_handler, events.NewMessage(pattern=f"^{prefix_cmds}eventauto(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("azai_auto_events")
