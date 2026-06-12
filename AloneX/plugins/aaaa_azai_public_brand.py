import os
import time
from datetime import datetime

import psutil
import pytz
from telethon import Button, events

from AloneX import START_TIME, database, font, prefix_cmds, tbot

try:
    from config import GROQ_API_KEY
except Exception:
    GROQ_API_KEY = "0"


IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
UPDATES_LINK = "https://t.me/EGOxUPDATES"
SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
MASTER_LINK = "https://t.me/EGOISTICxPRIME"


def readable_time(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def has_key(value: str) -> bool:
    value = str(value or "").strip()
    return bool(value and value.lower() not in {"0", "none", "null", "false", "your_groq_key", "your_groq_api_key"})


def groq_key() -> str:
    return GROQ_API_KEY or os.getenv("GROQ_API_KEY") or os.getenv("GRQI_API_KEY") or os.getenv("GQRI_API_KEY") or "0"


def ai_brain_status() -> str:
    return font("Active") if has_key(groq_key()) else font("Not Connected")


async def database_status() -> str:
    try:
        await database.command("ping")
        return font("Connected")
    except Exception:
        return font("Not Connected")


def buttons():
    return [
        [Button.url(font("Updates"), UPDATES_LINK), Button.url(font("Support"), SUPPORT_LINK)],
        [Button.url(font("My Master"), MASTER_LINK)],
    ]


def support_buttons():
    return [
        [Button.url(font("Support"), SUPPORT_LINK), Button.url(font("Updates"), UPDATES_LINK)],
        [Button.url(font("Owner"), MASTER_LINK), Button.inline(font("Close"), b"azai_status_close")],
    ]


async def alive_handler(event):
    uptime = readable_time(time.time() - START_TIME)
    now = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    cpu = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory().percent
    text = (
        font("AZAI IS ALIVE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Network:") + f" {BRAND}\n"
        + font("Owner:") + " " + font("MR EGO") + "\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Time:") + f" {now}\n"
        + font("CPU:") + f" {cpu:.1f}%\n"
        + font("RAM:") + f" {ram:.1f}%"
    )
    await event.reply(text, buttons=buttons())
    raise events.StopPropagation


async def ping_handler(event):
    start = time.perf_counter()
    msg = await event.reply(font("AZAI health check in progress..."))
    end = round((time.perf_counter() - start) * 1000, 2)
    uptime = readable_time(time.time() - START_TIME)
    now = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    cpu = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory().percent
    quality = font("Excellent") if end < 120 else font("Stable") if end < 350 else font("Slow")
    db_status = await database_status()
    ai_status = ai_brain_status()

    text = (
        font("AZAI SYSTEM STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Ping:") + f" {end} ms\n"
        + font("Quality:") + f" {quality}\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Database:") + f" {db_status}\n"
        + font("AI Brain:") + f" {ai_status}\n"
        + font("Network:") + f" {BRAND}\n"
        + font("Owner:") + " " + font("MR EGO") + "\n\n"
        + font("Server") + "\n"
        + font("CPU:") + f" {cpu:.1f}%\n"
        + font("RAM:") + f" {ram:.1f}%\n"
        + font("Checked At:") + f" {now}\n\n"
        + font("Need help? Use the Support button below.")
    )
    await msg.edit(text, buttons=support_buttons())
    raise events.StopPropagation


async def repo_handler(event):
    text = (
        font("AZAI SOURCE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("This is a private EGO Network system.") + "\n"
        + font("Public source link is not available.")
    )
    await event.reply(text, buttons=buttons())
    raise events.StopPropagation


async def close_callback(event):
    try:
        await event.answer(font("Closed."), alert=False)
    except Exception:
        pass
    try:
        await event.delete()
    except Exception:
        pass


if "aaaa_azai_public_brand" not in tbot.handlers_loaded:
    tbot.add_event_handler(alive_handler, events.NewMessage(pattern=f"^{prefix_cmds}alive(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(ping_handler, events.NewMessage(pattern=f"^{prefix_cmds}ping(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(repo_handler, events.NewMessage(pattern=f"^{prefix_cmds}repo(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(close_callback, events.CallbackQuery(data=b"azai_status_close"))
    tbot.handlers_loaded.add("aaaa_azai_public_brand")
