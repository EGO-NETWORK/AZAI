from datetime import datetime

from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import OWNER_ID

festival_db = database["azai_festivals"]

CALENDAR = [
    ("01/01", "all", "New Year", "Happy New Year from EGO Network.", 100),
    ("13/01", "sikh", "Lohri", "Warm wishes on Lohri from EGO Network.", 150),
    ("14/01", "hindu", "Makar Sankranti", "Happy Makar Sankranti from EGO Network.", 150),
    ("15/01", "hindu", "Pongal", "Happy Pongal from EGO Network.", 150),
    ("26/01", "all", "Republic Day", "Happy Republic Day from EGO Network.", 100),
    ("14/04", "all", "Ambedkar Jayanti", "Respect and remembrance from EGO Network.", 100),
    ("01/05", "all", "Labour Day", "Respect to every hardworking person.", 100),
    ("15/08", "all", "Independence Day", "Happy Independence Day from EGO Network.", 100),
    ("05/09", "all", "Teachers' Day", "Respect to teachers and mentors.", 100),
    ("02/10", "all", "Gandhi Jayanti", "Remembering values of truth and peace.", 100),
    ("26/11", "all", "Constitution Day", "Respect to justice, liberty, and equality.", 100),
    ("25/12", "christian", "Christmas", "Merry Christmas from EGO Network.", 150),
]


def owner_ids():
    try:
        owner = int(OWNER_ID)
        return {owner} if owner else set()
    except Exception:
        return set()


async def is_owner(event):
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


async def loadcalendarfull(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    year = raw[1].strip() if len(raw) > 1 else str(datetime.now().year)
    loaded = 0
    for date, religion, title, text, reward in CALENDAR:
        await festival_db.update_one(
            {"chat_id": int(event.chat_id), "title": title, "year": year},
            {"$set": {"chat_id": int(event.chat_id), "date": date, "religion": religion, "title": title, "text": text, "reward": reward, "year": year, "source": "azai_full_calendar"}},
            upsert=True,
        )
        loaded += 1
    await event.reply(font("AZAI calendar loaded:") + f" {year}\nLoaded: {loaded}\nUse /addfestival for yearly movable dates.")
    raise events.StopPropagation


async def calendarfullstatus(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    year = raw[1].strip() if len(raw) > 1 else str(datetime.now().year)
    total = await festival_db.count_documents({"chat_id": int(event.chat_id), "year": year, "source": "azai_full_calendar"})
    await event.reply(font("AZAI calendar status") + f"\nYear: {year}\nLoaded: {total}")
    raise events.StopPropagation


if "zzzzzz_azai_full_calendar_pack" not in tbot.handlers_loaded:
    tbot.add_event_handler(loadcalendarfull, events.NewMessage(pattern=f"^{prefix_cmds}loadcalendarfull(?: .*)?$", incoming=True))
    tbot.add_event_handler(calendarfullstatus, events.NewMessage(pattern=f"^{prefix_cmds}calendarfullstatus(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("zzzzzz_azai_full_calendar_pack")
