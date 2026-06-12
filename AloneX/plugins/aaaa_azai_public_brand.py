import time
from datetime import datetime

import psutil
import pytz
from telethon import Button, events

from AloneX import START_TIME, font, prefix_cmds, tbot

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


def buttons():
    return [[Button.url(font("Updates"), UPDATES_LINK), Button.url(font("Support"), SUPPORT_LINK)], [Button.url(font("My Master"), MASTER_LINK)]]


def support_buttons():
    return [[Button.url(font("Support"), SUPPORT_LINK)], [Button.url(font("Updates"), UPDATES_LINK), Button.url(font("My Master"), MASTER_LINK)]]


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
    msg = await event.reply(font("Checking AZAI latency..."))
    end = round((time.perf_counter() - start) * 1000, 2)
    uptime = readable_time(time.time() - START_TIME)
    now = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    cpu = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory().percent
    text = (
        font("AZAI SYSTEM PING") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Status:") + " " + font("Online") + "\n"
        + font("Response:") + f" {end} ms\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Time:") + f" {now}\n"
        + font("CPU:") + f" {cpu:.1f}%\n"
        + font("RAM:") + f" {ram:.1f}%\n\n"
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


if "aaaa_azai_public_brand" not in tbot.handlers_loaded:
    tbot.add_event_handler(alive_handler, events.NewMessage(pattern=f"^{prefix_cmds}alive(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(ping_handler, events.NewMessage(pattern=f"^{prefix_cmds}ping(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(repo_handler, events.NewMessage(pattern=f"^{prefix_cmds}repo(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aaaa_azai_public_brand")
