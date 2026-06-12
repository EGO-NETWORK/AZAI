from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
event_db = database["azai_events"]
bday_db = database["azai_" + "birthdays"]


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


def parse_date(value):
    value = str(value or "").strip().replace("-", "/")
    if "/" not in value:
        return None
    day_text, month_text = value.split("/", 1)
    if not day_text.isdigit() or not month_text.isdigit():
        return None
    day = int(day_text)
    month = int(month_text)
    try:
        datetime(2024, month, day)
    except ValueError:
        return None
    return day, month, f"{day:02d}/{month:02d}"


async def events_panel(event):
    text = (
        font("AZAI EVENTS PANEL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("User Commands") + "\n"
        + "/birthday DD/MM\n"
        + "/birthdays\n"
        + "/todayevents\n\n"
        + font("Owner Commands") + "\n"
        + "/addevent DD/MM | title | text\n"
        + "/delevent title\n"
        + "/eventauto on | off | status"
    )
    await event.reply(text)
    raise events.StopPropagation


async def add_event_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /addevent DD/MM | title | text"))
        raise events.StopPropagation
    parts = [x.strip() for x in raw[1].split("|", 2)]
    if len(parts) < 3:
        await event.reply(font("Use: /addevent DD/MM | title | text"))
        raise events.StopPropagation
    parsed = parse_date(parts[0])
    if not parsed:
        await event.reply(font("Invalid date. Use DD/MM."))
        raise events.StopPropagation
    day, month, date_key = parsed
    title = parts[1][:80]
    text = parts[2][:700]
    await event_db.update_one(
        {"key": title.lower()},
        {"$set": {"key": title.lower(), "title": title, "text": text, "day": day, "month": month, "date": date_key}},
        upsert=True,
    )
    await event.reply(font("Event saved.") + f"\n{font('Title:')} {title}\n{font('Date:')} {date_key}")
    raise events.StopPropagation


async def delete_event_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /delevent title"))
        raise events.StopPropagation
    result = await event_db.delete_one({"key": raw[1].strip().lower()})
    await event.reply(font("Event deleted.") if result.deleted_count else font("Event not found."))
    raise events.StopPropagation


async def today_events_handler(event):
    now = datetime.now(IST)
    rows = await event_db.find({"day": now.day, "month": now.month}).to_list(length=50)
    saved = await bday_db.find({"day": now.day, "month": now.month}).to_list(length=50)
    lines = [font("AZAI TODAY EVENTS"), "━━━━━━━━━━━━━━━━━━━━━━━━━━━━", f"{font('Date:')} {now.day:02d}/{now.month:02d}", ""]
    if saved:
        lines.append(font("Special Dates"))
        for index, row in enumerate(saved, 1):
            lines.append(f"{index}. {row.get('name', 'User')}")
        lines.append("")
    if rows:
        lines.append(font("Events"))
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. {font(row.get('title', 'Event'))}")
            lines.append(str(row.get("text", ""))[:250])
    if not rows and not saved:
        lines.append(font("No saved records for today."))
    await event.reply("\n".join(lines))
    raise events.StopPropagation


if "azai_events" not in tbot.handlers_loaded:
    tbot.add_event_handler(events_panel, events.NewMessage(pattern=f"^{prefix_cmds}events(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(today_events_handler, events.NewMessage(pattern=f"^{prefix_cmds}todayevents(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(add_event_handler, events.NewMessage(pattern=f"^{prefix_cmds}addevent(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(delete_event_handler, events.NewMessage(pattern=f"^{prefix_cmds}delevent(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("azai_events")
