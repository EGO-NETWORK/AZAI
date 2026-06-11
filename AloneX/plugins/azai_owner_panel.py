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
        + font("Control Center:") + " " + font("Core status, modules, launch checklist, and setup guide") + "\n\n"
        + font("Private data is hidden. Secrets are never shown here.") + "\n\n"
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
    groq_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY") or os.getenv("GRQI_API_KEY") or os.getenv("GQRI_API_KEY")
    status = font("Configured") if has_value(groq_key) else font("Missing")
    return (
        font("AI STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Provider:") + " " + font("Groq") + "\n"
        + font("Memory:") + " " + font("Short context enabled") + "\n"
        + font("Key Status:") + f" {status}\n"
        + font("Accepted env:") + " GROQ_API_KEY / GRQI_API_KEY / GQRI_API_KEY\n"
        + font("Secret Safety:") + " " + font("Hidden") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def logs_status_text() -> str:
    return (
        font("LOGGER STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Logger:") + " " + font("Allowed by owner control") + "\n"
        + font("Controls:") + " /logon /logoff /logstatus\n"
        + font("Note:") + " LOG_GROUP_ID must be numeric.\n\n"
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


def security_text() -> str:
    return (
        font("SECURITY CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Verification:") + " /verify /verifyall /unverifyall\n"
        + font("Moderation:") + " /mod /warn /mute /ban\n"
        + font("Anti-link:") + " /antilink on | off\n"
        + font("Removed shortcuts:") + " /prop /weds /ageverify guarded\n\n"
        + font("Use these in group where AZAI is admin.")
    )


def economy_text() -> str:
    return (
        font("ECONOMY CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Wallet:") + " /wallet /daily /send\n"
        + font("Inventory:") + " /inventory /garage /vault\n"
        + font("Market:") + " /shop /setcar /setbike /gift\n"
        + font("Referral:") + " /refer /redeemref\n"
        + font("Vault Items:") + " /addvaultitem /vaultitems /buyvault /myvault\n\n"
        + font("Currency:") + " EGO CREDIT (EC)"
    )


def quiz_text() -> str:
    return (
        font("QUIZ CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Easy add steps:") + "\n"
        + "1. Send anime/character image\n"
        + "2. Reply to that image\n"
        + "3. Use this:\n"
        + "/addanimeq Naruto | Naruto | Luffy | Gojo | Eren\n\n"
        + font("Play:") + " /animeguess /quiz\n"
        + font("Stats:") + " /quizstats /quiztop\n"
        + font("Auto:") + " /quizon /quizoff\n\n"
        + font("Reward:") + " +100 EC +15 XP, 5 streak = +200 EC"
    )


def market_text() -> str:
    return (
        font("MARKET MEDIA CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Set start panel image:") + "\n"
        + "1. Send image/video\n2. Reply to it\n3. /setstartpic\n\n"
        + font("Set item image:") + "\n"
        + "1. Send item image\n2. Reply to it\n3. /setitempic item_id\n\n"
        + font("Examples:") + "\n"
        + "/setitempic bike_splendor\n"
        + "/setitempic car_scorpio_s11_black\n"
        + "/setitempic rose\n\n"
        + font("Set vehicles after buy:") + "\n"
        + "/garage\n/setbike bike_splendor\n/setcar car_scorpio_s11_black"
    )


def guide_text() -> str:
    return (
        font("AZAI SETUP GUIDE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("START PIC:") + "\n"
        + "Send image/video -> reply -> /setstartpic\n\n"
        + font("ITEM PICS:") + "\n"
        + "Send item image -> reply -> /setitempic item_id\n"
        + "Example: /setitempic bike_splendor\n\n"
        + font("ANIME QUIZ:") + "\n"
        + "Send quiz image -> reply -> /addanimeq answer | option1 | option2 | option3 | option4\n"
        + "Example: /addanimeq Naruto | Naruto | Luffy | Gojo | Eren\n\n"
        + font("VEHICLE SET:") + "\n"
        + "/garage -> copy ID -> /setbike bike_id or /setcar car_id\n\n"
        + font("VAULT ITEM:") + "\n"
        + "/addvaultitem id | name | price | stock\n"
        + "Example: /addvaultitem royal_crown | Royal Crown | 5000 | 10\n\n"
        + font("BROADCAST:") + "\n"
        + "/broadcast text\n/broadcastpin text\n\n"
        + font("AI KEY:") + "\n"
        + "Replit Secrets me GROQ_API_KEY ya GRQI_API_KEY add karo."
    )


def launch_text() -> str:
    return (
        font("LAUNCH CHECKLIST") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "1. " + font("Restart bot after latest repo update") + "\n"
        + "2. " + font("Test /start and /commands") + "\n"
        + "3. " + font("Test /settings and /msettings") + "\n"
        + "4. " + font("Test /verify and group admin permissions") + "\n"
        + "5. " + font("Set start and item images") + "\n"
        + "6. " + font("Add 3-5 anime quiz questions") + "\n"
        + "7. " + font("Test /wallet /daily /shop /garage /broadcast") + "\n"
        + "8. " + font("Fix errors for 1-2 days, then publish")
    )


def maintenance_text() -> str:
    return (
        font("MAINTENANCE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Runtime restart must be done from hosting panel for now.") + "\n"
        + font("Recommended before launch:") + "\n"
        + "• " + font("Restart") + "\n"
        + "• " + font("Check logs") + "\n"
        + "• " + font("Run live group test") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def owner_buttons():
    return [
        [Button.inline(font("Guide"), b"azown_guide"), Button.inline(font("Bot Status"), b"azown_bot")],
        [Button.inline(font("AI Status"), b"azown_ai"), Button.inline(font("Database"), b"azown_db")],
        [Button.inline(font("Logs"), b"azown_logs"), Button.inline(font("Security"), b"azown_security")],
        [Button.inline(font("Economy"), b"azown_economy"), Button.inline(font("Quiz"), b"azown_quiz")],
        [Button.inline(font("Market Media"), b"azown_market"), Button.inline(font("Launch Check"), b"azown_launch")],
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
    elif data == "azown_guide":
        await event.edit(guide_text(), buttons=back_buttons())
    elif data == "azown_bot":
        await event.edit(bot_status_text(), buttons=back_buttons())
    elif data == "azown_ai":
        await event.edit(ai_status_text(), buttons=back_buttons())
    elif data == "azown_logs":
        await event.edit(logs_status_text(), buttons=back_buttons())
    elif data == "azown_db":
        await event.edit(database_status_text(), buttons=back_buttons())
    elif data == "azown_security":
        await event.edit(security_text(), buttons=back_buttons())
    elif data == "azown_economy":
        await event.edit(economy_text(), buttons=back_buttons())
    elif data == "azown_quiz":
        await event.edit(quiz_text(), buttons=back_buttons())
    elif data == "azown_market":
        await event.edit(market_text(), buttons=back_buttons())
    elif data == "azown_launch":
        await event.edit(launch_text(), buttons=back_buttons())
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
