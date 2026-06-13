import json
from datetime import datetime
from pathlib import Path

from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

festival_db = database["azai_festivals"]
CALENDAR_DIR = Path(__file__).resolve().parents[1] / "data"
ALLOWED_TYPES = {"hindu", "muslim", "christian", "sikh", "buddhist", "jain", "all"}


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


def valid_ddmm(value: str):
    try:
        datetime.strptime(value.strip(), "%d/%m")
        return value.strip()
    except Exception:
        return None


def clean_type(value: str):
    value = (value or "").strip().lower()
    return value if value in ALLOWED_TYPES else None


def get_path(year: str):
    year = "".join(ch for ch in str(year) if ch.isdigit())[:4]
    if not year:
        return None
    return year, CALENDAR_DIR / f"indian_calendar_{year}.json"


async def load_calendar(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    year = raw[1].strip() if len(raw) > 1 else str(datetime.now().year)
    res = get_path(year)
    if not res:
        await event.reply(font("Invalid year."))
        raise events.StopPropagation
    year, path = res
    if not path.exists():
        await event.reply(font("Calendar file missing:") + f" indian_calendar_{year}.json")
        raise events.StopPropagation
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("festivals", data) if isinstance(data, dict) else data
    loaded = 0
    skipped = 0
    for item in rows:
        if not isinstance(item, dict):
            skipped += 1
            continue
        date = valid_ddmm(str(item.get("date", "")))
        ftype = clean_type(str(item.get("religion", "all")))
        title = str(item.get("title", "")).strip()[:80]
        text = str(item.get("text", "")).strip()[:700]
        reward = int(item.get("reward", 100) or 100)
        reward = max(0, min(reward, 5000))
        if not date or not ftype or not title or not text:
            skipped += 1
            continue
        await festival_db.update_one(
            {"chat_id": int(event.chat_id), "title": title, "year": year},
            {"$set": {"chat_id": int(event.chat_id), "date": date, "religion": ftype, "title": title, "text": text, "reward": reward, "year": year, "source": "calendar_file"}},
            upsert=True,
        )
        loaded += 1
    await event.reply(font("Calendar loaded:") + f" {year}\nLoaded: {loaded}\nSkipped: {skipped}")
    raise events.StopPropagation


async def calendar_status(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    year = raw[1].strip() if len(raw) > 1 else str(datetime.now().year)
    res = get_path(year)
    year, path = res if res else (year, None)
    total = await festival_db.count_documents({"chat_id": int(event.chat_id), "year": str(year), "source": "calendar_file"})
    exists = bool(path and path.exists())
    await event.reply(font("Calendar status") + f"\nYear: {year}\nFile: {exists}\nLoaded: {total}")
    raise events.StopPropagation


if "zzzz_azai_calendar_loader" not in tbot.handlers_loaded:
    tbot.add_event_handler(load_calendar, events.NewMessage(pattern=f"^{prefix_cmds}loadcalendar(?: .*)?$", incoming=True))
    tbot.add_event_handler(calendar_status, events.NewMessage(pattern=f"^{prefix_cmds}calendarstatus(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("zzzz_azai_calendar_loader")
