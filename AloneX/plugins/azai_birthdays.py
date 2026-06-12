from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
bday_db = database["azai_birthdays"]


def parse_bday(value):
    value = str(value or "").strip().replace("-", "/")
    if "/" not in value:
        return None
    d, m = value.split("/", 1)
    if not d.isdigit() or not m.isdigit():
        return None
    day = int(d)
    month = int(m)
    try:
        datetime(2024, month, day)
    except ValueError:
        return None
    return day, month, f"{day:02d}/{month:02d}"


async def birthday_handler(event):
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /birthday DD/MM"))
        raise events.StopPropagation
    parsed = parse_bday(raw[1])
    if not parsed:
        await event.reply(font("Invalid date. Use DD/MM."))
        raise events.StopPropagation
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return
    day, month, date_key = parsed
    name = getattr(sender, "first_name", None) or "User"
    await bday_db.update_one(
        {"user_id": int(sender.id)},
        {"$set": {"user_id": int(sender.id), "name": name, "day": day, "month": month, "date": date_key}},
        upsert=True,
    )
    await event.reply(font("Birthday saved.") + f"\n{font('Date:')} {date_key}")
    raise events.StopPropagation


async def birthday_today_handler(event):
    now = datetime.now(IST)
    rows = await bday_db.find({"day": now.day, "month": now.month}).to_list(length=50)
    if not rows:
        await event.reply(font("No saved birthdays today."))
        raise events.StopPropagation
    lines = [font("AZAI BIRTHDAYS TODAY"), "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
    for index, row in enumerate(rows, 1):
        lines.append(f"{index}. {row.get('name', 'User')}")
    await event.reply("\n".join(lines))
    raise events.StopPropagation


if "azai_birthdays" not in tbot.handlers_loaded:
    tbot.add_event_handler(birthday_handler, events.NewMessage(pattern=f"^{prefix_cmds}birthday(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(birthday_today_handler, events.NewMessage(pattern=f"^{prefix_cmds}birthdays(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("azai_birthdays")
