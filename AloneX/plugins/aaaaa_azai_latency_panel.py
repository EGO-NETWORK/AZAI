import time
from telethon import Button, events

from AloneX import START_TIME, font, prefix_cmds, tbot

SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
UPDATES_LINK = "https://t.me/EGOxUPDATES"
CMD = "pi" + "ng"


def readable_time(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def buttons():
    return [[Button.url(font("Support"), SUPPORT_LINK), Button.url(font("Updates"), UPDATES_LINK)]]


async def latency_panel(event):
    start = time.time()
    msg = await event.reply(font("Checking AZAI system..."))
    speed = round((time.time() - start) * 1000, 2)
    state = font("Excellent") if speed < 250 else font("Stable") if speed < 600 else font("Slow")
    text = (
        font("AZAI SYSTEM STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Network:") + " " + font("EGO Network - EST. 2026") + "\n"
        + font("Owner:") + " " + font("MR EGO") + "\n"
        + font("Status:") + f" {state}\n"
        + font("Response:") + f" {speed} ms\n"
        + font("Uptime:") + f" {readable_time(time.time() - START_TIME)}\n\n"
        + font("Support is available below.")
    )
    await msg.edit(text, buttons=buttons())
    raise events.StopPropagation


if "aaaaa_azai_latency_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(latency_panel, events.NewMessage(pattern=rf"^[{prefix_cmds}]{CMD}(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aaaaa_azai_latency_panel")
