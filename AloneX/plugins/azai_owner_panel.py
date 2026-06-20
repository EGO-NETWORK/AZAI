import os
import time
from datetime import datetime

import psutil
import pytz
from telethon import Button, events

from AloneX import START_TIME, database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, GROQ_API_KEY, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")

wallet_db = database["azai_wallets"]
rep_db = database["azai_reputation"]
ref_db = database["azai_referrals"]


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


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


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
        + font("Control Center:") + " " + font("Core status, modules, launch checklist, setup guide, and reset controls") + "\n\n"
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
        + font("Note:") + " LOG_GROUP_ID " + font("must be numeric.") + "\n\n"
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
        + font("Owner Reset:") + " " + font("Use Reset Economy button from owner panel") + "\n"
        + font("Reset Scope:") + " balance, XP, level, REP, message count, daily claim date\n"
        + font("Safe:") + " inventory, garage, vault, and items are not deleted\n\n"
        + font("Currency:") + " EGO CREDIT (EC)"
    )


def reset_economy_warning_text() -> str:
    return (
        font("RESET ECONOMY") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("This will reset for all users:") + "\n"
        + "• Balance / EC\n"
        + "• XP / Level / rank values\n"
        + "• REP and REP daily records\n"
        + "• Message reward count\n"
        + "• Daily claim date\n\n"
        + font("This will NOT delete:") + "\n"
        + "• Inventory\n"
        + "• Garage / selected vehicles\n"
        + "• Vault / limited items\n"
        + "• Market items\n\n"
        + font("Press Confirm only if you really want a clean launch economy.")
    )


async def reset_economy_data() -> dict:
    now = now_ist()
    wallet_result = await wallet_db.update_many(
        {},
        {
            "$set": {
                "balance": 0,
                "xp": 0,
                "level": 1,
                "rep": 0,
                "messages": 0,
                "daily_at": None,
                "updated_at": now,
            },
            "$unset": {
                "rank": "",
                "rank_points": "",
                "power": "",
                "protection": "",
                "protection_until": "",
                "protect_until": "",
                "raid_wins": "",
                "attack_wins": "",
                "fight_wins": "",
                "heist_wins": "",
                "last_work": "",
                "last_luck": "",
                "last_heist": "",
                "work_at": "",
                "luck_at": "",
                "heist_at": "",
            },
        },
    )
    rep_result = await rep_db.delete_many({})

    extra_counts = {}
    for col_name in (
        "azai_hustle_stats",
        "azai_hustle_cooldowns",
        "azai_economy_cooldowns",
        "azai_work_cooldowns",
        "azai_luck_cooldowns",
        "azai_heist_cooldowns",
        "azai_protection",
    ):
        try:
            res = await database[col_name].delete_many({})
            if res.deleted_count:
                extra_counts[col_name] = res.deleted_count
        except Exception:
            pass

    return {
        "wallets": int(wallet_result.modified_count),
        "matched_wallets": int(wallet_result.matched_count),
        "rep_logs": int(rep_result.deleted_count),
        "extra": extra_counts,
    }


def reset_done_text(stats: dict) -> str:
    extra = stats.get("extra") or {}
    extra_text = ""
    if extra:
        extra_text = "\n" + "\n".join(f"• {k}: {v}" for k, v in extra.items())
    return (
        font("ECONOMY RESET DONE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Wallets matched:") + f" {stats.get('matched_wallets', 0)}\n"
        + font("Wallets updated:") + f" {stats.get('wallets', 0)}\n"
        + font("REP logs deleted:") + f" {stats.get('rep_logs', 0)}"
        + extra_text + "\n\n"
        + font("Inventory, garage, vault, and market items were kept safe.")
    )


def reset_buttons():
    return [
        [Button.inline(font("Confirm Reset"), b"azown_reseteco_confirm")],
        [Button.inline(font("Cancel"), b"azown_home")],
    ]


def quiz_text() -> str:
    return (
        font("QUIZ CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Anime quiz is disabled for rebuild.") + "\n"
        + font("MR EGO will add the new quiz system later.")
    )


def market_text() -> str:
    return (
        font("MARKET MEDIA CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Set start panel image:") + "\n"
        + font("1. Send image or video") + "\n"
        + font("2. Reply to it") + "\n"
        + font("3. Use command:") + " /setstartpic\n\n"
        + font("Set item image:") + "\n"
        + font("1. Send item image") + "\n"
        + font("2. Reply to it") + "\n"
        + font("3. Use command:") + " /setitempic item_id\n\n"
        + font("Examples:") + "\n"
        + "/setitempic bike_splendor\n"
        + "/setitempic car_scorpio_s11_black\n"
        + "/setitempic rose\n\n"
        + font("Set vehicles after buy:") + "\n"
        + "/garage\n/setbike bike_splendor\n/setcar car_scorpio_s11_black"
    )


def events_text() -> str:
    return (
        font("EVENT CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Panel:") + " /events\n"
        + font("Birthday:") + " /birthday DD/MM /birthdays\n"
        + font("Today:") + " /todayevents\n"
        + font("Owner Add:") + " /addevent DD/MM | title | text\n"
        + font("Owner Delete:") + " /delevent title\n"
        + font("Auto Wish:") + " /eventauto on | off | status\n\n"
        + font("Status:") + " " + font("Event, saved-date, and auto-wish modules active.")
    )


def games_text() -> str:
    return (
        font("GAME CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Panel:") + " /games\n"
        + font("Commands:") + " /dice /dart /basketball\n"
        + font("Rule:") + " " + font("Free clean mini-games only.") + "\n\n"
        + font("Status:") + " " + font("Game panel and basic handlers active.")
    )


def guide_text() -> str:
    return (
        font("AZAI SETUP GUIDE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("START PIC:") + "\n"
        + font("Send image or video, reply to it, then use:") + " /setstartpic\n\n"
        + font("ITEM PICS:") + "\n"
        + font("Send item image, reply to it, then use:") + " /setitempic item_id\n"
        + font("Example:") + " /setitempic bike_splendor\n\n"
        + font("EVENTS:") + "\n"
        + "/events\n"
        + "/addevent DD/MM | title | text\n"
        + "/eventauto status\n\n"
        + font("AI KEY:") + "\n"
        + font("Replit Secrets me") + " GROQ_API_KEY / GRQI_API_KEY " + font("add karo.")
    )


def launch_text() -> str:
    return (
        font("LAUNCH CHECKLIST") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "1. " + font("Restart bot after latest repo update") + "\n"
        + "2. " + font("Test") + " /start /commands\n"
        + "3. " + font("Test") + " /owner /events /wallet\n"
        + "4. " + font("Test verification and group admin permissions") + "\n"
        + "5. " + font("Set start and item images") + "\n"
        + "6. " + font("Reset economy before public launch if needed") + "\n"
        + "7. " + font("Test") + " /wallet /daily /shop /garage /broadcast\n"
        + "8. " + font("Test") + " /eventauto status /todayevents\n"
        + "9. " + font("Fix errors for 1-2 days, then publish")
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
        [Button.inline(font("Economy"), b"azown_economy"), Button.inline(font("Reset Economy"), b"azown_reseteco")],
        [Button.inline(font("Quiz"), b"azown_quiz"), Button.inline(font("Events"), b"azown_events")],
        [Button.inline(font("Games"), b"azown_games"), Button.inline(font("Market Media"), b"azown_market")],
        [Button.inline(font("Launch Check"), b"azown_launch"), Button.inline(font("Commands"), b"azown_commands")],
        [Button.inline(font("Maintenance"), b"azown_maintenance"), Button.inline(font("Close"), b"azown_close")],
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
    elif data == "azown_reseteco":
        await event.edit(reset_economy_warning_text(), buttons=reset_buttons())
    elif data == "azown_reseteco_confirm":
        await event.edit(font("Resetting economy... please wait."))
        stats = await reset_economy_data()
        await event.edit(reset_done_text(stats), buttons=back_buttons())
    elif data == "azown_quiz":
        await event.edit(quiz_text(), buttons=back_buttons())
    elif data == "azown_events":
        await event.edit(events_text(), buttons=back_buttons())
    elif data == "azown_games":
        await event.edit(games_text(), buttons=back_buttons())
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
    tbot.add_event_handler(owner_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}owner(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(owner_callback, events.CallbackQuery(pattern=b"^azown_"))
    tbot.handlers_loaded.add("azai_owner_panel")
