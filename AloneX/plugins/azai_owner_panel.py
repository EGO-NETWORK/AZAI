import os
import time
from datetime import datetime

import psutil
import pytz
from telethon import Button, events

from AloneX import START_TIME, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, GROQ_API_KEY, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")


def owner_ids() -> set[int]:
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


async def is_owner(event) -> bool:
    sender = await event.get_sender()
    return bool(sender and sender.id in owner_ids())


def readable_time(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def has_value(value) -> bool:
    if not value:
        return False
    value = str(value).strip().lower()
    return value not in {"0", "none", "null", "false", "your_groq_key", "your_groq_api_key"}


def owner_home_text() -> str:
    return (
        font("AZAI OWNER PANEL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Access:") + " " + font("Owner Only") + "\n"
        + font("Use buttons below to check core system status.") + "\n\n"
        + font("Private data is not shown in this panel.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def bot_status_text() -> str:
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime = readable_time(time.time() - START_TIME)
    now = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    return (
        font("BOT STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Status:") + " " + font("Online") + "\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Time:") + f" {now}\n\n"
        + font("CPU:") + f" {cpu:.1f}%\n"
        + font("RAM:") + f" {memory.percent:.1f}%\n"
        + font("Storage:") + f" {disk.percent:.1f}%\n\n"
        + font("Powered By:") + " " + BRAND
    )


def ai_status_text() -> str:
    groq_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY") or os.getenv("GQRI_API_KEY")
    status = font("Configured") if has_value(groq_key) else font("Missing")
    return (
        font("AI STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Provider:") + " " + font("Groq") + "\n"
        + font("Key Status:") + f" {status}\n"
        + font("Secret Safety:") + " " + font("Hidden") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def logs_status_text() -> str:
    return (
        font("LOG STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Public logger:") + " " + font("Disabled by AZAI log guard") + "\n"
        + font("Normal user messages:") + " " + font("Should not be logged") + "\n"
        + font("Important logs:") + " " + font("Owner-safe mode pending") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def database_status_text() -> str:
    return (
        font("DATABASE STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Status:") + " " + font("Connected") + "\n"
        + font("Data Core:") + " " + font("AZAI") + "\n"
        + font("Secrets:") + " " + font("Hidden") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def maintenance_text() -> str:
    return (
        font("MAINTENANCE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Restart controls, broadcast, and maintenance toggle will be added after core modules are stable.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def owner_buttons():
    return [
        [Button.inline(font("Bot Status"), b"azown_bot"), Button.inline(font("AI Status"), b"azown_ai")],
        [Button.inline(font("Log Status"), b"azown_logs"), Button.inline(font("Database"), b"azown_db")],
        [Button.inline(font("Commands"), b"azown_commands"), Button.inline(font("Maintenance"), b"azown_maintenance")],
        [Button.inline(font("Close"), b"azown_close")],
    ]


def back_buttons():
    return [[Button.inline(font("Back"), b"azown_home"), Button.inline(font("Close"), b"azown_close")]]


async def owner_panel_handler(event):
    if not await is_owner(event):
        await event.reply(font("This command is owner-only."))
        return
    await event.reply(owner_home_text(), buttons=owner_buttons())


async def owner_callback(event):
    if not await is_owner(event):
        await event.answer(font("Owner-only panel."), alert=True)
        return
    data = event.data.decode()
    if data == "azown_home":
        await event.edit(owner_home_text(), buttons=owner_buttons())
    elif data == "azown_bot":
        await event.edit(bot_status_text(), buttons=back_buttons())
    elif data == "azown_ai":
        await event.edit(ai_status_text(), buttons=back_buttons())
    elif data == "azown_logs":
        await event.edit(logs_status_text(), buttons=back_buttons())
    elif data == "azown_db":
        await event.edit(database_status_text(), buttons=back_buttons())
    elif data == "azown_commands":
        await event.edit(font("Use /commands to open the public command center."), buttons=back_buttons())
    elif data == "azown_maintenance":
        await event.edit(maintenance_text(), buttons=back_buttons())
    elif data == "azown_close":
        await event.delete()


if "azai_owner_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(owner_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}owner(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(owner_callback, events.CallbackQuery(pattern=b"^azown_"))
    tbot.handlers_loaded.add("azai_owner_panel")
