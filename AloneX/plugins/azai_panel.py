import time
from datetime import datetime

import psutil
import pytz
from telethon import Button, events

from AloneX import START_TIME, BOT_USERNAME, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
AZAI_PANEL_MEDIA = "https://files.catbox.moe/1gxuh7.jpg"
UPDATES_LINK = "https://t.me/EGOxUPDATES"
SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
MASTER_LINK = "https://t.me/EGOISTICxPRIME"
AZAI_BOT_USERNAME = "Urxazaibot"


def readable_time(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def bot_username_clean() -> str:
    username = str(BOT_USERNAME or "").replace("@", "").strip()
    if not username or username.lower() in {"azai", "oxnybot", "eiko"}:
        username = AZAI_BOT_USERNAME
    return username


def add_to_group_link() -> str:
    return f"https://t.me/{bot_username_clean()}?startgroup=true"


def azai_home_text() -> str:
    uptime = readable_time(time.time() - START_TIME)
    ist_time = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    return (
        font("❂ AZAI IS ONLINE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Network:") + " `EGO Network - EST. 2026`\n"
        + font("Owner:") + " `MR EGO`\n"
        + font("Uptime:") + f" `{uptime}`\n"
        + font("Time:") + f" `{ist_time}`\n\n"
        + font("Summon AZAI To Your Empire") + "\n"
        + font("Turn your group into a royal command center with protection, rewards, quizzes, events, and premium EGO Network control.") + "\n\n"
        + font("Core: Verification, AI Chat, Economy, Quiz, Shop, Vault, Events.") + "\n\n"
        + font("Powered By:") + " `EGO Network - EST. 2026`"
    )


def azai_help_text() -> str:
    return (
        "❂ **AZAI HELP MENU**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Security:** Verification, Anti-Spam, Warnings, Group Control\n"
        "**Profile:** Profile Setup, Cards, Titles, Badges\n"
        "**Economy:** Ego Credits, XP, REP, Daily Rewards\n"
        "**Quiz:** Anime Quiz, GK Quiz, Auto Quiz\n"
        "**Shop:** Items, Images, Gifts, Permanent Vault\n"
        "**Events:** Birthday Wishes, Festival Wishes, Custom Events\n"
        "**Media:** Start Media, Premium Panels, Button Controls\n\n"
        "**Powered By:** `EGO Network - EST. 2026`"
    )


def azai_buttons():
    return [
        [Button.inline(font("❂ Help"), b"azai_help_menu"), Button.inline(font("❂ System Stats"), b"azai_system_stats")],
        [Button.url(font("❂ Add AZAI To Your Empire"), add_to_group_link())],
        [Button.url(font("❂ Updates"), UPDATES_LINK), Button.url(font("❂ Support"), SUPPORT_LINK)],
        [Button.url(font("❂ My Master"), MASTER_LINK), Button.inline(font("❂ Close"), b"azai_close_panel")],
    ]


def azai_help_buttons():
    return [
        [Button.url(font("❂ Add AZAI To Your Empire"), add_to_group_link())],
        [Button.inline(font("❂ Back"), b"azai_back_home"), Button.inline(font("❂ Close"), b"azai_close_panel")],
    ]


async def azai_panel_handler(event):
    if event.is_channel and not event.is_group:
        return
    if event.fwd_from:
        return
    await event.reply(azai_home_text(), file=AZAI_PANEL_MEDIA, buttons=azai_buttons())


async def azai_help_command(event):
    if event.is_channel and not event.is_group:
        return
    if event.fwd_from:
        return
    await event.reply(azai_help_text(), file=AZAI_PANEL_MEDIA, buttons=azai_help_buttons())


async def azai_help_menu(event):
    await event.answer(font("Opening AZAI help menu..."))
    await event.edit(azai_help_text(), buttons=azai_help_buttons(), file=AZAI_PANEL_MEDIA)


async def azai_system_stats(event):
    await event.answer(font("Loading AZAI system stats..."))
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime = readable_time(time.time() - START_TIME)
    ist_time = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    text = (
        "❂ **AZAI SYSTEM STATS**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Brand:** `EGO Network - EST. 2026`\n\n"
        "**Performance:**\n"
        f"• **CPU:** `{cpu:.1f}%`\n"
        f"• **RAM:** `{memory.percent:.1f}%`\n"
        f"• **Storage:** `{disk.percent:.1f}%`\n\n"
        "**Runtime:**\n"
        f"• **Uptime:** `{uptime}`\n"
        f"• **Time:** `{ist_time}`"
    )
    buttons = [
        [Button.inline(font("❂ Back"), b"azai_back_home"), Button.inline(font("❂ Refresh"), b"azai_system_stats")],
        [Button.inline(font("❂ Close"), b"azai_close_panel")],
    ]
    await event.edit(text, buttons=buttons)


async def azai_back_home(event):
    await event.answer()
    await event.edit(azai_home_text(), buttons=azai_buttons(), file=AZAI_PANEL_MEDIA)


async def azai_close_panel(event):
    await event.delete()
    await event.answer(font("AZAI panel closed."))


if "azai_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(azai_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}start(?: .*)?$", incoming=True))
    tbot.add_event_handler(azai_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}azai$", incoming=True))
    tbot.add_event_handler(azai_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}startpanel$", incoming=True))
    tbot.add_event_handler(azai_help_command, events.NewMessage(pattern=f"^{prefix_cmds}help$", incoming=True))
    tbot.add_event_handler(azai_help_menu, events.CallbackQuery(pattern=b"azai_help_menu"))
    tbot.add_event_handler(azai_system_stats, events.CallbackQuery(pattern=b"azai_system_stats"))
    tbot.add_event_handler(azai_back_home, events.CallbackQuery(pattern=b"azai_back_home"))
    tbot.add_event_handler(azai_close_panel, events.CallbackQuery(pattern=b"azai_close_panel"))
    tbot.handlers_loaded.add("azai_panel")
