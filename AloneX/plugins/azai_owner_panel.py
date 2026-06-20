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
anime_auto_db = database["azai_anime_quiz_auto_clean"]
owner_override_db = database["azai_owner_override_mod"]


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
        + font("Control Center:") + " " + font("Core status, security, quiz, economy, launch, and owner override controls") + "\n\n"
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


async def owner_mod_status_line(chat_id: int) -> str:
    row = await owner_override_db.find_one({"chat_id": int(chat_id)}) or {}
    return "ON" if row.get("enabled") else "OFF"


async def set_owner_mod(chat_id: int, enabled: bool, user_id: int = 0):
    await owner_override_db.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"chat_id": int(chat_id), "enabled": bool(enabled), "updated_by": int(user_id or 0), "updated_at": now_ist()}},
        upsert=True,
    )


async def owner_mod_text(chat_id: int) -> str:
    status = await owner_mod_status_line(chat_id)
    return (
        font("OWNER OVERRIDE MOD") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Status:") + f" {status}\n"
        + font("Only:") + " MR EGO / owner ID\n\n"
        + font("Commands:") + "\n"
        + "/ownermod on\n"
        + "/ownermod off\n"
        + "/ownermod status\n\n"
        + font("Phrases:") + "\n"
        + "azai nikal = ban target\n"
        + "azai chup = mute target\n\n"
        + font("Target:") + " reply or @username\n"
        + font("Bot Requirement:") + " AZAI must be admin with ban/mute permission"
    )


def owner_mod_buttons():
    return [
        [Button.inline(font("Owner Mod ON"), b"azown_ownermod_on"), Button.inline(font("Owner Mod OFF"), b"azown_ownermod_off")],
        [Button.inline(font("Owner Mod Status"), b"azown_ownermod_status")],
        [Button.inline(font("Back"), b"azown_home"), Button.inline(font("Close"), b"azown_close")],
    ]


async def security_text(chat_id: int) -> str:
    owner_mod = await owner_mod_status_line(chat_id)
    return (
        font("SECURITY CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Verification:") + " /verify /verifyall /unverifyall\n"
        + font("Moderation:") + " /mod /warn /mute /ban /kick /purge\n"
        + font("Anti-link:") + " /antilink on | off\n"
        + font("Owner Override:") + f" {owner_mod}\n"
        + font("Owner Mod:") + " /ownermod on /ownermod off /ownermod status\n\n"
        + font("Use these in group where AZAI is admin.")
    )


def security_buttons():
    return [
        [Button.inline(font("Owner Mod"), b"azown_owner_mod")],
        [Button.inline(font("Back"), b"azown_home"), Button.inline(font("Close"), b"azown_close")],
    ]


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
        {"$set": {"balance": 0, "xp": 0, "level": 1, "rep": 0, "messages": 0, "daily_at": None, "updated_at": now}, "$unset": {"rank": "", "rank_points": "", "power": "", "protection": "", "protection_until": "", "protect_until": "", "raid_wins": "", "attack_wins": "", "fight_wins": "", "heist_wins": "", "last_work": "", "last_luck": "", "last_heist": "", "work_at": "", "luck_at": "", "heist_at": ""}},
    )
    rep_result = await rep_db.delete_many({})
    extra_counts = {}
    for col_name in ("azai_hustle_stats", "azai_hustle_cooldowns", "azai_economy_cooldowns", "azai_work_cooldowns", "azai_luck_cooldowns", "azai_heist_cooldowns", "azai_protection"):
        try:
            res = await database[col_name].delete_many({})
            if res.deleted_count:
                extra_counts[col_name] = res.deleted_count
        except Exception:
            pass
    return {"wallets": int(wallet_result.modified_count), "matched_wallets": int(wallet_result.matched_count), "rep_logs": int(rep_result.deleted_count), "extra": extra_counts}


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
    return [[Button.inline(font("Confirm Reset"), b"azown_reseteco_confirm")], [Button.inline(font("Cancel"), b"azown_home")]]


async def quiz_auto_status_line(chat_id: int) -> str:
    row = await anime_auto_db.find_one({"chat_id": int(chat_id)}) or {}
    enabled = bool(row.get("enabled", False))
    next_at = int(row.get("next_at") or 0)
    wait = max(next_at - int(time.time()), 0) if enabled else 0
    return f"Auto: {'ON' if enabled else 'OFF'} | Next: {wait // 60}m {wait % 60}s"


async def quiz_text(chat_id: int) -> str:
    status = await quiz_auto_status_line(chat_id)
    return (
        font("ANIME QUIZ CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Add Image Quiz:") + " /addanimeq answer | option1 | option2 | option3 | option4\n"
        + font("Play One Quiz:") + " /animeguess /quiz\n"
        + font("Stats:") + " /quizstats /quiztop\n"
        + font("Owner:") + " /quizlist /delanimeq question_id\n"
        + font("Auto:") + " every 30 minutes\n"
        + font("Status:") + f" {status}\n\n"
        + font("Rule:") + " one saved quiz at a time, never all together\n"
        + font("Reward:") + " 150 EC + 15 XP"
    )


def quiz_buttons():
    return [[Button.inline(font("Auto ON"), b"azown_quizauto_on"), Button.inline(font("Auto OFF"), b"azown_quizauto_off")], [Button.inline(font("Auto Status"), b"azown_quizauto_status")], [Button.inline(font("Back"), b"azown_home"), Button.inline(font("Close"), b"azown_close")]]


async def set_quiz_auto(chat_id: int, enabled: bool, user_id: int = 0):
    now = int(time.time())
    await anime_auto_db.update_one({"chat_id": int(chat_id)}, {"$set": {"chat_id": int(chat_id), "enabled": bool(enabled), "interval": 1800, "next_at": now + 1800 if enabled else None, "updated_by": int(user_id or 0), "updated_at": now_ist()}}, upsert=True)


def market_text() -> str:
    return (
        font("MARKET MEDIA CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Set start panel image:") + "\n"
        + font("Send image/video, reply, then use:") + " /setstartpic\n\n"
        + font("Set item image:") + "\n"
        + font("Send item image, reply, then use:") + " /setitempic item_id\n\n"
        + font("EGO HUSTLE MEDIA:") + "\n"
        + "/sethustlemedia panel\n"
        + "/sethustlemedia work\n"
        + "/sethustlemedia raid\n"
        + "/sethustlemedia protect\n"
        + "/sethustlemedia luck\n"
        + "/sethustlemedia heist"
    )


def events_text() -> str:
    return font("EVENT CONTROL") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Panel:") + " /events\n" + font("Birthday:") + " /birthday DD/MM /birthdays\n" + font("Owner Add:") + " /addevent DD/MM | title | text\n" + font("Auto Wish:") + " /eventauto on | off | status"


def games_text() -> str:
    return font("GAME CONTROL") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Panel:") + " /games\n" + font("Commands:") + " /dice /dart /basketball\n" + font("EGO HUSTLE:") + " /hustle /work /raid /protect /luck /heist"


def guide_text() -> str:
    return (
        font("AZAI SETUP GUIDE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("OWNER MOD:") + "\n/ownermod on\n/ownermod off\n/ownermod status\n"
        + font("Phrases:") + " azai nikal / azai chup\n\n"
        + font("EGO HUSTLE MEDIA:") + "\n/sethustlemedia panel\n/sethustlemedia work\n/sethustlemedia raid\n/sethustlemedia protect\n/sethustlemedia luck\n/sethustlemedia heist\n\n"
        + font("ANIME QUIZ:") + "\n/addanimeq answer | option1 | option2 | option3 | option4\n/animeguess\n\n"
        + font("EVENTS:") + "\n/events\n/addevent DD/MM | title | text\n"
    )


def launch_text() -> str:
    return font("LAUNCH CHECKLIST") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. " + font("Restart bot after latest repo update") + "\n2. " + font("Test") + " /start /commands\n3. " + font("Test") + " /owner /events /wallet /ownermod status\n4. " + font("Test") + " /hustle /work /luck /heist\n5. " + font("Set media") + " /sethustlemedia panel|work|raid|protect|luck|heist\n6. " + font("Run live group test")


def maintenance_text() -> str:
    return font("MAINTENANCE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Runtime restart must be done from hosting panel for now.")


def owner_buttons():
    return [
        [Button.inline(font("Guide"), b"azown_guide"), Button.inline(font("Bot Status"), b"azown_bot")],
        [Button.inline(font("AI Status"), b"azown_ai"), Button.inline(font("Database"), b"azown_db")],
        [Button.inline(font("Security"), b"azown_security"), Button.inline(font("Owner Mod"), b"azown_owner_mod")],
        [Button.inline(font("Economy"), b"azown_economy"), Button.inline(font("Reset Economy"), b"azown_reseteco")],
        [Button.inline(font("Quiz"), b"azown_quiz"), Button.inline(font("Events"), b"azown_events")],
        [Button.inline(font("Games"), b"azown_games"), Button.inline(font("Market Media"), b"azown_market")],
        [Button.inline(font("Launch Check"), b"azown_launch"), Button.inline(font("Maintenance"), b"azown_maintenance")],
        [Button.inline(font("Logs"), b"azown_logs"), Button.inline(font("Close"), b"azown_close")],
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
        await event.edit(await security_text(event.chat_id), buttons=security_buttons())
    elif data == "azown_owner_mod":
        await event.edit(await owner_mod_text(event.chat_id), buttons=owner_mod_buttons())
    elif data == "azown_ownermod_on":
        sender = await event.get_sender()
        await set_owner_mod(event.chat_id, True, sender.id if sender else 0)
        await event.edit(await owner_mod_text(event.chat_id), buttons=owner_mod_buttons())
    elif data == "azown_ownermod_off":
        sender = await event.get_sender()
        await set_owner_mod(event.chat_id, False, sender.id if sender else 0)
        await event.edit(await owner_mod_text(event.chat_id), buttons=owner_mod_buttons())
    elif data == "azown_ownermod_status":
        await event.answer(await owner_mod_status_line(event.chat_id), alert=True)
    elif data == "azown_economy":
        await event.edit(economy_text(), buttons=back_buttons())
    elif data == "azown_reseteco":
        await event.edit(reset_economy_warning_text(), buttons=reset_buttons())
    elif data == "azown_reseteco_confirm":
        await event.edit(font("Resetting economy... please wait."))
        stats = await reset_economy_data()
        await event.edit(reset_done_text(stats), buttons=back_buttons())
    elif data == "azown_quiz":
        await event.edit(await quiz_text(event.chat_id), buttons=quiz_buttons())
    elif data == "azown_quizauto_on":
        sender = await event.get_sender()
        await set_quiz_auto(event.chat_id, True, sender.id if sender else 0)
        await event.edit(await quiz_text(event.chat_id), buttons=quiz_buttons())
    elif data == "azown_quizauto_off":
        sender = await event.get_sender()
        await set_quiz_auto(event.chat_id, False, sender.id if sender else 0)
        await event.edit(await quiz_text(event.chat_id), buttons=quiz_buttons())
    elif data == "azown_quizauto_status":
        await event.answer(await quiz_auto_status_line(event.chat_id), alert=True)
    elif data == "azown_events":
        await event.edit(events_text(), buttons=back_buttons())
    elif data == "azown_games":
        await event.edit(games_text(), buttons=back_buttons())
    elif data == "azown_market":
        await event.edit(market_text(), buttons=back_buttons())
    elif data == "azown_launch":
        await event.edit(launch_text(), buttons=back_buttons())
    elif data == "azown_maintenance":
        await event.edit(maintenance_text(), buttons=back_buttons())
    elif data == "azown_close":
        await event.delete()


if "azai_owner_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(owner_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}owner(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(owner_callback, events.CallbackQuery(pattern=b"^azown_"))
    tbot.handlers_loaded.add("azai_owner_panel")
