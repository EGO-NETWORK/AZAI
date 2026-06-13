from datetime import datetime

from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

festival_db = database["azai_festivals"]

CALENDAR = [
    ("01/01", "all", "New Year", "Happy New Year from EGO Network."),
    ("13/01", "sikh", "Lohri", "Warm wishes on Lohri from EGO Network."),
    ("14/01", "hindu", "Makar Sankranti", "Happy Makar Sankranti from EGO Network."),
    ("26/01", "all", "Republic Day", "Happy Republic Day from EGO Network."),
    ("14/04", "all", "Ambedkar Jayanti", "Remembering Dr. B. R. Ambedkar from EGO Network."),
    ("15/08", "all", "Independence Day", "Happy Independence Day from EGO Network."),
    ("02/10", "all", "Gandhi Jayanti", "Remembering Mahatma Gandhi from EGO Network."),
    ("14/11", "all", "Children's Day", "Happy Children's Day from EGO Network."),
    ("25/12", "christian", "Christmas", "Merry Christmas from EGO Network."),
]


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


async def loadcalendar_builtin(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    year = raw[1].strip() if len(raw) > 1 else str(datetime.now().year)
    loaded = 0
    for date, religion, title, text in CALENDAR:
        await festival_db.update_one(
            {"chat_id": int(event.chat_id), "title": title, "year": str(year)},
            {"$set": {"chat_id": int(event.chat_id), "date": date, "religion": religion, "title": title, "text": text, "reward": 500, "year": str(year), "source": "builtin_indian_calendar"}},
            upsert=True,
        )
        loaded += 1
    await event.reply(font("Indian calendar loaded:") + f" {year}\nLoaded: {loaded}\nReward: 500 EC")
    raise events.StopPropagation


async def calendarstatus_builtin(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    year = raw[1].strip() if len(raw) > 1 else str(datetime.now().year)
    total = await festival_db.count_documents({"chat_id": int(event.chat_id), "year": str(year), "source": "builtin_indian_calendar"})
    await event.reply(font("Indian calendar status") + f"\nYear: {year}\nLoaded: {total}\nReward: 500 EC")
    raise events.StopPropagation


if "zzzz_azai_aaa_builtin_calendar" not in tbot.handlers_loaded:
    tbot.add_event_handler(loadcalendar_builtin, events.NewMessage(pattern=f"^{prefix_cmds}loadcalendar(?: .*)?$", incoming=True))
    tbot.add_event_handler(calendarstatus_builtin, events.NewMessage(pattern=f"^{prefix_cmds}calendarstatus(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("zzzz_azai_aaa_builtin_calendar")
