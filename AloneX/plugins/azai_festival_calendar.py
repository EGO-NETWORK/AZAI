import asyncio
from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
festival_db = database["azai_festival_calendar"]
chat_db = database["azai_broadcast_chats"]
log_db = database["azai_festival_logs"]
setting_db = database["azai_festival_settings"]

DEFAULT_FESTIVALS = [
    {"day": 1, "month": 1, "name": "New Year", "text": "Wishing everyone a fresh, positive, and successful year."},
    {"day": 14, "month": 1, "name": "Makar Sankranti", "text": "Wishing everyone happiness, respect, and positive energy."},
    {"day": 15, "month": 1, "name": "Army Day", "text": "Respect and salute to the brave hearts of India."},
    {"day": 26, "month": 1, "name": "Republic Day", "text": "Celebrating the Constitution, unity, and pride of India."},
    {"day": 30, "month": 1, "name": "Martyrs Day", "text": "Respectful remembrance for those who served the nation."},
    {"day": 14, "month": 2, "name": "Valentine Day", "text": "Wishing everyone love, kindness, and respect."},
    {"day": 8, "month": 3, "name": "International Women's Day", "text": "Respect, strength, and appreciation for women everywhere."},
    {"day": 4, "month": 3, "name": "Holi", "text": "Wishing everyone a joyful and colorful Holi."},
    {"day": 20, "month": 3, "name": "Eid al-Fitr", "text": "Wishing peace, blessings, and happiness to everyone celebrating."},
    {"day": 22, "month": 3, "name": "Ugadi / Gudi Padwa", "text": "Wishing a bright and positive new beginning."},
    {"day": 26, "month": 3, "name": "Ram Navami", "text": "Wishing peace, devotion, and strength."},
    {"day": 3, "month": 4, "name": "Mahavir Jayanti", "text": "Wishing peace, non-violence, and wisdom."},
    {"day": 14, "month": 4, "name": "Ambedkar Jayanti", "text": "Respecting justice, equality, and knowledge."},
    {"day": 14, "month": 4, "name": "Baisakhi", "text": "Wishing prosperity, joy, and new energy."},
    {"day": 3, "month": 5, "name": "Buddha Purnima", "text": "Wishing peace, compassion, and wisdom."},
    {"day": 27, "month": 5, "name": "Eid al-Adha", "text": "Wishing peace, blessings, and togetherness."},
    {"day": 21, "month": 6, "name": "International Yoga Day", "text": "Wishing health, balance, and discipline."},
    {"day": 6, "month": 7, "name": "Muharram", "text": "A day of remembrance, reflection, and respect."},
    {"day": 26, "month": 7, "name": "Kargil Vijay Diwas", "text": "Salute to the courage and sacrifice of our soldiers."},
    {"day": 15, "month": 8, "name": "Independence Day", "text": "Celebrating freedom, unity, and pride of India."},
    {"day": 19, "month": 8, "name": "Raksha Bandhan", "text": "Wishing love, protection, and respect among families."},
    {"day": 4, "month": 9, "name": "Janmashtami", "text": "Wishing devotion, joy, and peace."},
    {"day": 14, "month": 9, "name": "Hindi Diwas", "text": "Respecting the beauty and pride of Hindi language."},
    {"day": 17, "month": 9, "name": "Vishwakarma Puja", "text": "Respecting skill, craft, machines, and hard work."},
    {"day": 21, "month": 9, "name": "Eid Milad-un-Nabi", "text": "Wishing peace, kindness, and blessings."},
    {"day": 2, "month": 10, "name": "Gandhi Jayanti", "text": "Remembering truth, peace, and simplicity."},
    {"day": 20, "month": 10, "name": "Dussehra", "text": "Wishing victory of good values and courage."},
    {"day": 31, "month": 10, "name": "National Unity Day", "text": "Celebrating unity, strength, and togetherness."},
    {"day": 1, "month": 11, "name": "Karwa Chauth", "text": "Wishing respect, care, and family happiness."},
    {"day": 8, "month": 11, "name": "Diwali", "text": "Wishing light, prosperity, happiness, and clean positive energy."},
    {"day": 9, "month": 11, "name": "Govardhan Puja", "text": "Wishing devotion, gratitude, and prosperity."},
    {"day": 10, "month": 11, "name": "Bhai Dooj", "text": "Wishing love and respect between brothers and sisters."},
    {"day": 15, "month": 11, "name": "Guru Nanak Jayanti", "text": "Wishing peace, equality, and service."},
    {"day": 26, "month": 11, "name": "Constitution Day", "text": "Respecting justice, rights, and responsibility."},
    {"day": 4, "month": 12, "name": "Navy Day", "text": "Respect and salute to the Indian Navy."},
    {"day": 25, "month": 12, "name": "Christmas", "text": "Wishing peace, kindness, and happiness."},
    {"day": 31, "month": 12, "name": "Year End", "text": "Wishing everyone a safe and positive year ending."},
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


async def seed_defaults():
    for item in DEFAULT_FESTIVALS:
        key = item["name"].lower()
        data = dict(item)
        data["key"] = key
        data["default"] = True
        await festival_db.update_one({"key": key}, {"$setOnInsert": data}, upsert=True)


async def enabled():
    data = await setting_db.find_one({"key": "main"})
    if not data:
        return True
    return bool(data.get("enabled", True))


async def set_enabled(value):
    await setting_db.update_one({"key": "main"}, {"$set": {"key": "main", "enabled": bool(value)}}, upsert=True)


def festival_message(rows, date_text):
    lines = [font("AZAI FESTIVAL WISH"), "━━━━━━━━━━━━━━━━━━━━━━━━━━━━", font("Date:") + f" {date_text}", ""]
    for index, row in enumerate(rows, 1):
        lines.append(f"{index}. {font(row.get('name', 'Festival'))}")
        text = row.get("text") or "Wishing everyone happiness, respect, and positivity."
        lines.append(font(text))
        lines.append("")
    lines.append(font("Powered By:") + " " + font("EGO Network"))
    return "\n".join(lines)


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


async def todays_festivals():
    now = datetime.now(IST)
    rows = await festival_db.find({"day": now.day, "month": now.month}).to_list(length=50)
    return now, rows


async def festival_auto_once():
    if not await enabled():
        return
    await seed_defaults()
    now, rows = await todays_festivals()
    date_key = now.strftime("%Y-%m-%d")
    if await log_db.find_one({"date": date_key}):
        return
    if not rows:
        await log_db.update_one({"date": date_key}, {"$set": {"date": date_key, "count": 0}}, upsert=True)
        return
    date_text = f"{now.day:02d}/{now.month:02d}"
    text = festival_message(rows, date_text)
    chats = await chat_db.find({"type": "group"}).to_list(length=5000)
    sent = 0
    failed = 0
    for chat in chats:
        if await send_group(chat.get("chat_id"), text):
            sent += 1
        else:
            failed += 1
    await log_db.update_one({"date": date_key}, {"$set": {"date": date_key, "count": len(rows), "sent": sent, "failed": failed}}, upsert=True)


async def loop_runner():
    await asyncio.sleep(25)
    while True:
        try:
            await festival_auto_once()
        except Exception:
            pass
        await asyncio.sleep(1800)


async def festivals_handler(event):
    await seed_defaults()
    rows = await festival_db.find({}).sort([("month", 1), ("day", 1)]).to_list(length=200)
    text = font("AZAI FESTIVAL CALENDAR") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for row in rows[:80]:
        text += f"{int(row.get('day', 0)):02d}/{int(row.get('month', 0)):02d} - {row.get('name', 'Festival')}\n"
    text += "\n" + font("Owner commands:") + "\n/addfestival DD/MM | name | wish\n/delfestival name\n/festivalauto on | off | status"
    await event.reply(text)
    raise events.StopPropagation


async def today_festivals_handler(event):
    await seed_defaults()
    now, rows = await todays_festivals()
    date_text = f"{now.day:02d}/{now.month:02d}"
    if rows:
        await event.reply(festival_message(rows, date_text))
    else:
        await event.reply(font("No festival saved for today.") + f"\n{font('Date:')} {date_text}")
    raise events.StopPropagation


async def add_festival_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use:") + " /addfestival DD/MM | name | wish")
        raise events.StopPropagation
    parts = [x.strip() for x in raw[1].split("|", 2)]
    if len(parts) < 3:
        await event.reply(font("Use:") + " /addfestival DD/MM | name | wish")
        raise events.StopPropagation
    parsed = parse_date(parts[0])
    if not parsed:
        await event.reply(font("Invalid date. Use DD/MM."))
        raise events.StopPropagation
    day, month, date_key = parsed
    name = parts[1][:80]
    wish = parts[2][:500]
    key = name.lower()
    await festival_db.update_one({"key": key}, {"$set": {"key": key, "day": day, "month": month, "date": date_key, "name": name, "text": wish, "default": False}}, upsert=True)
    await event.reply(font("Festival saved.") + f"\n{font('Name:')} {name}\n{font('Date:')} {date_key}")
    raise events.StopPropagation


async def delete_festival_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use:") + " /delfestival name")
        raise events.StopPropagation
    result = await festival_db.delete_one({"key": raw[1].strip().lower()})
    await event.reply(font("Festival deleted.") if result.deleted_count else font("Festival not found."))
    raise events.StopPropagation


async def festival_auto_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    mode = raw[1].strip().lower() if len(raw) > 1 else "status"
    if mode == "on":
        await set_enabled(True)
        await event.reply(font("Festival auto wishes enabled."))
    elif mode == "off":
        await set_enabled(False)
        await event.reply(font("Festival auto wishes disabled."))
    else:
        state = font("ON") if await enabled() else font("OFF")
        await event.reply(font("Festival auto wishes:") + f" {state}\n" + font("Use:") + " /festivalauto on | off | status")
    raise events.StopPropagation


if "azai_festival_calendar" not in tbot.handlers_loaded:
    try:
        tbot.loop.create_task(loop_runner())
    except Exception:
        pass
    tbot.add_event_handler(festivals_handler, events.NewMessage(pattern=f"^{prefix_cmds}festivals(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(today_festivals_handler, events.NewMessage(pattern=f"^{prefix_cmds}todayfestivals(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(add_festival_handler, events.NewMessage(pattern=f"^{prefix_cmds}addfestival(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(delete_festival_handler, events.NewMessage(pattern=f"^{prefix_cmds}delfestival(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(festival_auto_handler, events.NewMessage(pattern=f"^{prefix_cmds}festivalauto(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("azai_festival_calendar")
