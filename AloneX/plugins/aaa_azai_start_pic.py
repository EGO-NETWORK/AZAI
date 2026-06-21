import time
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import START_TIME, BOT_USERNAME, database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
media_db = database["azai_start_panel_pic"]
UPDATES_LINK = "https://t.me/EGOxUPDATES"
SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
MASTER_LINK = "https://t.me/EGOISTICxPRIME"
PRIVACY_LINK = "https://telegra.ph/EGO-NETWORK-LEGAL-NOTICE-06-11"
AZAI_BOT_USERNAME = "Urxazaibot"


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
    return bool(sender and int(sender.id) in owner_ids())


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


def brand() -> str:
    return font("EGO Network - EST. 2026")


def cmd_line(command: str, usage: str) -> str:
    return f"{command} - {font(usage)}\n"


def start_text() -> str:
    uptime = readable_time(time.time() - START_TIME)
    ist_time = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    return (
        font("AZAI IS ONLINE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Network:") + " " + brand() + "\n"
        + font("Owner:") + " " + font("MR EGO") + "\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Time:") + f" {ist_time}\n\n"
        + font("Protection, economy, market, and clean group control.") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def start_buttons():
    return [
        [Button.inline(font("Help & Cmds"), b"azai_help_cmds_menu"), Button.inline(font("System Stats"), b"azai_system_stats")],
        [Button.url(font("Add AZAI To Your Empire"), add_to_group_link())],
        [Button.url(font("Updates"), UPDATES_LINK), Button.url(font("Support"), SUPPORT_LINK)],
        [Button.url(font("Privacy"), PRIVACY_LINK)],
        [Button.url(font("My Master"), MASTER_LINK), Button.inline(font("Close"), b"azai_close_panel")],
    ]


def close_back_buttons():
    return [[Button.inline(font("Help Menu"), b"azai_help_cmds_menu"), Button.inline(font("Close"), b"azai_close_panel")]]


def home_back_buttons():
    return [[Button.inline(font("Back"), b"azai_start_home"), Button.inline(font("Close"), b"azai_close_panel")]]


def help_buttons():
    return [
        [Button.inline(font("Core"), b"azai_help_core"), Button.inline(font("Owner"), b"azai_help_owner")],
        [Button.inline(font("Economy"), b"azai_help_economy"), Button.inline(font("Market"), b"azai_help_market")],
        [Button.inline(font("Family"), b"azai_help_family"), Button.inline(font("Games"), b"azai_help_games")],
        [Button.inline(font("Media"), b"azai_help_media"), Button.inline(font("System"), b"azai_system_stats")],
        [Button.inline(font("Back"), b"azai_start_home"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


def help_text() -> str:
    return (
        font("AZAI HELP & COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a panel below.") + "\n"
        + font("Each command includes its use in English.") + "\n\n"
        + font("Core, Owner, Economy, Market, Family, Games, Media, System")
    )


def core_text() -> str:
    return (
        font("CORE COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + cmd_line("/start", "Open the official AZAI start panel")
        + cmd_line("/help", "Open the help and command menu")
        + cmd_line("/ping", "Check bot response speed")
        + cmd_line("/alive", "Check if AZAI is online")
        + cmd_line("/repo", "Show project repository information")
    )


def owner_text() -> str:
    return (
        font("OWNER COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + cmd_line("/owner", "Open MR EGO owner control panel")
        + cmd_line("/settings", "Open group settings panel")
        + cmd_line("/msettings", "Open media settings panel")
        + cmd_line("/broadcast", "Send an official broadcast")
        + cmd_line("/logstatus", "Check logger status")
        + cmd_line("/logon", "Enable private and group logger")
        + cmd_line("/logoff", "Disable private and group logger")
    )


def economy_text() -> str:
    return (
        font("ECONOMY COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + cmd_line("/wallet", "Open your wallet panel")
        + cmd_line("/balance or /bal", "Check your EC balance and XP")
        + cmd_line("/daily", "Claim your daily EC reward")
        + cmd_line("/work", "Earn EC through activity jobs")
        + cmd_line("/send amount", "Transfer EC to another user by reply")
        + cmd_line("/leaderboard", "View the richest users leaderboard")
        + cmd_line("/inventory", "View your owned items")
    )


def market_text() -> str:
    return (
        font("MARKET COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + cmd_line("/shop", "Open the item shop")
        + cmd_line("/inventory", "View your purchased items")
        + cmd_line("/garage", "View your cars and bikes")
        + cmd_line("/setbike item_id", "Set your active bike")
        + cmd_line("/setcar item_id", "Set your active car")
        + cmd_line("/gift item_name", "Gift an item by replying to a user")
    )


def family_text() -> str:
    return (
        font("FAMILY COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + cmd_line("/brother", "Send a brother relation request")
        + cmd_line("/sister", "Send a sister relation request")
        + cmd_line("/adopt", "Send an adoption relation request")
        + cmd_line("/family", "View your saved family relations")
        + cmd_line("/familytree", "Open your family tree panel")
        + cmd_line("/leavefamily", "Leave your current family relation")
    )


def games_text() -> str:
    return (
        font("GAMES COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + cmd_line("/hustle", "Open EGO Hustle economy game panel")
        + cmd_line("/dice", "Play the Telegram dice mini game")
        + cmd_line("/dart", "Play the dart mini game")
        + cmd_line("/basketball", "Play the basketball mini game")
        + cmd_line("/slot", "Play the slot machine mini game")
        + "\n"
        + font("Use games in groups for fun, activity, and rewards.")
    )


def media_text() -> str:
    return (
        font("MEDIA COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + cmd_line("/setstartpic", "Set start and help panel media")
        + cmd_line("/setitempic item_id", "Attach media to a shop item")
        + cmd_line("/setleaderpic", "Set leaderboard media card")
        + cmd_line("/msettings", "Open media setup guide")
    )


def stats_text() -> str:
    uptime = readable_time(time.time() - START_TIME)
    ist_time = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    return (
        font("AZAI SYSTEM STATS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Status:") + " " + font("Online") + "\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Time:") + f" {ist_time}\n"
        + font("Network:") + " " + brand()
    )


async def saved_pic():
    data = await media_db.find_one({"key": "start"})
    if not data:
        return None
    try:
        msg = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        if msg and msg.media:
            return msg.media
    except Exception:
        return None
    return None


async def set_start_pic(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to start panel picture first."))
        raise events.StopPropagation
    await media_db.update_one({"key": "start"}, {"$set": {"key": "start", "chat_id": int(reply.chat_id), "msg_id": int(reply.id)}}, upsert=True)
    await event.reply(font("Start panel picture saved."))
    raise events.StopPropagation


async def start_pic_handler(event):
    pic = await saved_pic()
    if pic:
        await tbot.send_file(event.chat_id, pic, caption=start_text(), buttons=start_buttons())
    else:
        await event.reply(start_text(), buttons=start_buttons())
    raise events.StopPropagation


async def start_callback_handler(event):
    data = event.data.decode()
    if data == "azai_help_cmds_menu":
        await event.edit(help_text(), buttons=help_buttons())
    elif data == "azai_help_core":
        await event.edit(core_text(), buttons=close_back_buttons())
    elif data == "azai_help_owner":
        await event.edit(owner_text(), buttons=close_back_buttons())
    elif data == "azai_help_economy":
        await event.edit(economy_text(), buttons=close_back_buttons())
    elif data == "azai_help_market":
        await event.edit(market_text(), buttons=close_back_buttons())
    elif data == "azai_help_family":
        await event.edit(family_text(), buttons=close_back_buttons())
    elif data == "azai_help_games":
        await event.edit(games_text(), buttons=close_back_buttons())
    elif data == "azai_help_media":
        await event.edit(media_text(), buttons=close_back_buttons())
    elif data == "azai_system_stats":
        await event.edit(stats_text(), buttons=home_back_buttons())
    elif data == "azai_start_home":
        await event.edit(start_text(), buttons=start_buttons())
    elif data == "azai_close_panel":
        await event.delete()
    raise events.StopPropagation


if "aaa_azai_start_pic" not in tbot.handlers_loaded:
    tbot.add_event_handler(set_start_pic, events.NewMessage(pattern=f"^{prefix_cmds}setstartpic$", incoming=True))
    tbot.add_event_handler(start_pic_handler, events.NewMessage(pattern=f"^{prefix_cmds}start(?:@\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(start_pic_handler, events.NewMessage(pattern=f"^{prefix_cmds}help(?:@\w+)?$", incoming=True))
    tbot.add_event_handler(start_callback_handler, events.CallbackQuery(pattern=b"^azai_(help_cmds_menu|help_core|help_owner|help_economy|help_market|help_family|help_games|help_media|system_stats|start_home|close_panel)$"))
    tbot.handlers_loaded.add("aaa_azai_start_pic")
