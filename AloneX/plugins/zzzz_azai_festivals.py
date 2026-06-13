import asyncio
from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
festival_db = database["azai_festivals"]
settings_db = database["azai_event_settings"]
sent_db = database["azai_festival_sent"]
religion_db = database["azai_user_religions"]
wallet_db = database["azai_wallets"]

RELIGIONS = {"hindu", "muslim", "christian", "sikh", "buddhist", "jain", "all"}

DEFAULT_FESTIVALS = [
    ("01/01", "all", "New Year", "Happy New Year from EGO Network. Stay safe, grow strong, and keep moving forward.", 100),
    ("13/01", "sikh", "Lohri", "Warm wishes on Lohri. May this day bring happiness, light, and positive energy.", 150),
    ("14/01", "hindu", "Makar Sankranti", "Happy Makar Sankranti. May this festival bring light, progress, and good fortune.", 150),
    ("26/01", "all", "Republic Day", "Happy Republic Day. Respect, unity, and responsibility make a strong community.", 100),
    ("14/04", "all", "Ambedkar Jayanti", "Remembering Dr. B. R. Ambedkar and his message of equality, dignity, and education.", 100),
    ("15/08", "all", "Independence Day", "Happy Independence Day. Salute to freedom, unity, and the spirit of India.", 100),
    ("02/10", "all", "Gandhi Jayanti", "Remembering Mahatma Gandhi and the values of truth, peace, and discipline.", 100),
    ("14/11", "all", "Children's Day", "Happy Children's Day. Keep learning, keep growing, and keep your dreams alive.", 100),
    ("25/12", "christian", "Christmas", "Merry Christmas. May peace, kindness, and happiness stay with you.", 150),
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


def clean_religion(value: str):
    value = (value or "").strip().lower()
    if value in RELIGIONS:
        return value
    return None


async def safe_pin(chat_id: int, msg):
    if not msg or int(chat_id) > 0:
        return False
    try:
        await tbot.pin_message(chat_id, msg, notify=False)
        return True
    except Exception:
        return False


async def reward_user(user_id: int, amount: int):
    if amount <= 0:
        return
    try:
        await wallet_db.update_one({"user_id": int(user_id)}, {"$inc": {"balance": int(amount), "xp": 5}}, upsert=True)
    except Exception:
        pass


async def already_sent(key: str) -> bool:
    return bool(await sent_db.find_one({"key": key}))


async def mark_sent(key: str, chat_id: int, title: str):
    await sent_db.update_one({"key": key}, {"$set": {"key": key, "chat_id": int(chat_id), "title": title, "sent_at": int(now_ist().timestamp())}}, upsert=True)


async def matching_users(chat_id: int, religion: str):
    query = {"chat_id": int(chat_id)}
    if religion != "all":
        query["religion"] = religion
    return await religion_db.find(query).to_list(length=200)


async def send_festival(chat_id: int, row: dict):
    title = row.get("title") or "Festival"
    religion = row.get("religion") or "all"
    reward = int(row.get("reward", 0) or 0)
    key = f"{today_key()}:festival:{chat_id}:{title}"
    if await already_sent(key):
        return

    users = await matching_users(chat_id, religion)
    rewarded = 0
    for user in users:
        user_id = int(user.get("user_id"))
        await reward_user(user_id, reward)
        rewarded += 1
        try:
            await tbot.send_message(user_id, font(title) + "\n\n" + str(row.get("text", "")) + f"\n\nReward: +{reward} EC")
        except Exception:
            pass
        await asyncio.sleep(0.2)

    text = (
        font("AZAI FESTIVAL WISH")
        + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        + font(title)
        + "\n"
        + str(row.get("text", ""))
        + "\n\n"
        + font("Religion:")
        + f" {religion.title()}\n"
        + font("Rewarded:")
        + f" {rewarded} users"
    )
    if reward:
        text += f"\n+{reward} EC"

    msg = await tbot.send_message(chat_id, text)
    await safe_pin(chat_id, msg)
    await mark_sent(key, chat_id, title)


async def run_festivals_for_chat(chat_id: int):
    day = today_ddmm()
    rows = await festival_db.find({"chat_id": int(chat_id), "date": day}).to_list(length=30)
    for row in rows:
        try:
            await send_festival(int(chat_id), row)
            await asyncio.sleep(0.5)
        except Exception:
            pass


async def run_daily_festivals():
    cursor = settings_db.find({"auto": True})
    async for row in cursor:
        try:
            await run_festivals_for_chat(int(row.get("chat_id")))
            await asyncio.sleep(1)
        except Exception:
            pass


async def festival_loop():
    await asyncio.sleep(15)
    while True:
        try:
            if 8 <= now_ist().hour <= 22:
                await run_daily_festivals()
        except Exception:
            pass
        await asyncio.sleep(1800)


async def seedfestivals(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    count = 0
    for date, religion, title, text, reward in DEFAULT_FESTIVALS:
        await festival_db.update_one(
            {"chat_id": int(event.chat_id), "title": title},
            {"$set": {"chat_id": int(event.chat_id), "date": date, "religion": religion, "title": title, "text": text, "reward": int(reward)}},
            upsert=True,
        )
        count += 1
    await event.reply(font("Default festival pack added:") + f" {count}")
    raise events.StopPropagation


async def addfestival(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2 or "|" not in raw[1]:
        await event.reply(font("Use: /addfestival DD/MM | religion | title | wish text | reward"))
        raise events.StopPropagation
    parts = [x.strip() for x in raw[1].split("|")]
    if len(parts) < 4:
        await event.reply(font("Use: /addfestival DD/MM | religion | title | wish text | reward"))
        raise events.StopPropagation
    date = valid_ddmm(parts[0])
    religion = clean_religion(parts[1])
    if not date or not religion:
        await event.reply(font("Invalid date or religion."))
        raise events.StopPropagation
    title = parts[2][:80]
    text = parts[3][:700]
    try:
        reward = int(parts[4]) if len(parts) > 4 else 100
    except Exception:
        reward = 100
    reward = max(0, min(reward, 5000))
    await festival_db.update_one({"chat_id": int(event.chat_id), "title": title}, {"$set": {"chat_id": int(event.chat_id), "date": date, "religion": religion, "title": title, "text": text, "reward": reward}}, upsert=True)
    await event.reply(font("Festival saved:") + f" {title}")
    raise events.StopPropagation


async def delfestival(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /delfestival title"))
        raise events.StopPropagation
    res = await festival_db.delete_one({"chat_id": int(event.chat_id), "title": parts[1].strip()})
    await event.reply(font("Festival deleted." if res.deleted_count else "Festival not found."))
    raise events.StopPropagation


async def festivals(event):
    rows = await festival_db.find({"chat_id": int(event.chat_id)}).sort("date", 1).to_list(length=80)
    text = font("SAVED FESTIVALS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No festival saved. Use /seedfestivals or /addfestival.")
    else:
        for row in rows[:60]:
            text += f"{row.get('date')} - {row.get('title')} [{row.get('religion')}] +{row.get('reward', 0)} EC\n"
    await event.reply(text)
    raise events.StopPropagation


async def todayfestivals(event):
    day = today_ddmm()
    rows = await festival_db.find({"chat_id": int(event.chat_id), "date": day}).to_list(length=30)
    text = font("TODAY FESTIVALS") + f" - {day}\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No saved festival for today.")
    else:
        for row in rows:
            text += f"{row.get('title')} [{row.get('religion')}] +{row.get('reward', 0)} EC\n{row.get('text')}\n\n"
    await event.reply(text)
    raise events.StopPropagation


async def religion(event):
    sender = await event.get_sender()
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /religion hindu/muslim/christian/sikh/buddhist/jain/all"))
        raise events.StopPropagation
    value = clean_religion(raw[1])
    if not value:
        await event.reply(font("Invalid religion option."))
        raise events.StopPropagation
    await religion_db.update_one({"chat_id": int(event.chat_id), "user_id": int(sender.id)}, {"$set": {"chat_id": int(event.chat_id), "user_id": int(sender.id), "name": getattr(sender, "first_name", "Member") or "Member", "religion": value}}, upsert=True)
    await event.reply(font("Religion preference saved:") + f" {value.title()}")
    raise events.StopPropagation


async def myreligion(event):
    sender = await event.get_sender()
    row = await religion_db.find_one({"chat_id": int(event.chat_id), "user_id": int(sender.id)}) or {}
    value = row.get("religion") or "Not set"
    await event.reply(font("Your religion preference:") + f" {value}")
    raise events.StopPropagation


async def festivalauto(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = (event.raw_text or "").split(maxsplit=1)
    value = raw[1].strip().lower() if len(raw) > 1 else "status"
    if value in {"on", "off"}:
        await settings_db.update_one({"chat_id": int(event.chat_id)}, {"$set": {"chat_id": int(event.chat_id), "auto": value == "on"}}, upsert=True)
    elif value == "now":
        await run_festivals_for_chat(int(event.chat_id))
    data = await settings_db.find_one({"chat_id": int(event.chat_id)}) or {}
    status = font("On") if data.get("auto") else font("Off")
    await event.reply(font("Festival auto status:") + f" {status}")
    raise events.StopPropagation


if "zzzz_azai_festivals" not in tbot.handlers_loaded:
    tbot.add_event_handler(seedfestivals, events.NewMessage(pattern=f"^{prefix_cmds}seedfestivals(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(addfestival, events.NewMessage(pattern=f"^{prefix_cmds}addfestival(?: .*)?$", incoming=True))
    tbot.add_event_handler(delfestival, events.NewMessage(pattern=f"^{prefix_cmds}delfestival(?: .*)?$", incoming=True))
    tbot.add_event_handler(festivals, events.NewMessage(pattern=f"^{prefix_cmds}festivals(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(todayfestivals, events.NewMessage(pattern=f"^{prefix_cmds}todayfestivals(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(religion, events.NewMessage(pattern=f"^{prefix_cmds}religion(?: .*)?$", incoming=True))
    tbot.add_event_handler(myreligion, events.NewMessage(pattern=f"^{prefix_cmds}myreligion(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(festivalauto, events.NewMessage(pattern=f"^{prefix_cmds}festivalauto(?: .*)?$", incoming=True))
    try:
        tbot.loop.create_task(festival_loop())
    except Exception:
        pass
    tbot.handlers_loaded.add("zzzz_azai_festivals")
