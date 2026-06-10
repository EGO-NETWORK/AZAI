import time
from datetime import datetime

import psutil
import pytz
from telethon import Button, events

from AloneX import START_TIME, BOT_USERNAME, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
AZAI_PANEL_MEDIA = None
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


def brand() -> str:
    return font("EGO Network - EST. 2026")


def azai_home_text() -> str:
    uptime = readable_time(time.time() - START_TIME)
    ist_time = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    return (
        font("AZAI IS ONLINE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Network:") + " " + brand() + "\n"
        + font("Owner:") + " " + font("MR EGO") + "\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Time:") + f" {ist_time}\n\n"
        + font("Summon AZAI To Your Empire") + "\n"
        + font("Turn your group into a royal command center with protection, rewards, quizzes, events, and premium EGO Network control.") + "\n\n"
        + font("Core: Verification, AI Chat, Economy, Quiz, Shop, Vault, Events.") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def azai_help_cmds_text() -> str:
    return (
        font("AZAI HELP AND COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a category below to see commands and usage.") + "\n"
        + font("Owner-only commands stay hidden from public users.") + "\n\n"
        + font("Available: Core, Profile, Verify, Moderation, Economy, Market, Social, AI, Owner.") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def core_text() -> str:
    return (
        font("CORE COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/start - " + font("Open start panel") + "\n"
        + "/help - " + font("Open this help menu") + "\n"
        + "/commands - " + font("Open command center") + "\n"
        + "/group - " + font("Open group panel") + "\n"
        + "/settings - " + font("Open settings panel") + "\n"
        + "/rules - " + font("Show group rules") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def profile_text() -> str:
    return (
        font("PROFILE COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/setup - " + font("Create profile") + "\n"
        + "/profile - " + font("Show saved profile") + "\n"
        + "/setname - " + font("Save name") + "\n"
        + "/setgender - " + font("Save gender option") + "\n"
        + "/setbirthday - " + font("Save birthday date") + "\n"
        + "/setreligion - " + font("Save preference option") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def verify_text() -> str:
    return (
        font("VERIFY COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/verify - " + font("Verify yourself") + "\n"
        + "/verifyall - " + font("Admin group verify") + "\n"
        + "/unverifyall - " + font("Admin reset verify") + "\n"
        + "/verified - " + font("Show verified count") + "\n"
        + "/unverified - " + font("Show unverified count") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def mod_text() -> str:
    return (
        font("MODERATION COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/mod - " + font("Open moderation panel") + "\n"
        + "/antilink on/off - " + font("Toggle link guard") + "\n"
        + "/warn - " + font("Warn replied user") + "\n"
        + "/unwarn - " + font("Remove warning") + "\n"
        + "/warnings - " + font("Check warnings") + "\n"
        + "/resetwarns - " + font("Reset warnings") + "\n"
        + "/mute - " + font("Mute replied user") + "\n"
        + "/unmute - " + font("Unmute replied user") + "\n"
        + "/ban - " + font("Ban replied user") + "\n"
        + "/unban - " + font("Unban replied user") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def economy_text() -> str:
    return (
        font("ECONOMY COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/wallet - " + font("Show wallet") + "\n"
        + "/balance - " + font("Show balance") + "\n"
        + "/daily - " + font("Claim daily EC") + "\n"
        + "/send amount - " + font("Send EC by reply") + "\n"
        + "/rep - " + font("Give daily REP") + "\n"
        + "/myrep - " + font("Show REP") + "\n"
        + "/leaderboard - " + font("Show leaderboard") + "\n"
        + "/inventory - " + font("Show inventory") + "\n"
        + "/refer - " + font("Create referral code") + "\n"
        + "/redeemref CODE - " + font("Redeem referral code") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def market_text() -> str:
    return (
        font("MARKET COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/shop - " + font("Open market") + "\n"
        + "/garage - " + font("Show vehicles") + "\n"
        + "/vault - " + font("Open vault") + "\n"
        + "/setcar item_id - " + font("Set active car") + "\n"
        + "/setbike item_id - " + font("Set active bike") + "\n"
        + "/gift item_name - " + font("Send gift by reply") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def social_text() -> str:
    return (
        font("SOCIAL COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/ageverify - " + font("Confirm access for restricted social commands") + "\n"
        + "/prop - " + font("Send Prime Bond request by reply") + "\n"
        + "/weds - " + font("Send Duo Bond request by reply") + "\n"
        + "/brother - " + font("Send brother link request") + "\n"
        + "/sister - " + font("Send sister link request") + "\n"
        + "/adopt - " + font("Send member link request") + "\n"
        + "/family - " + font("Show saved links") + "\n"
        + "/familytree - " + font("Show profile buttons") + "\n"
        + "/leavefamily - " + font("Remove saved family links") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def ai_text() -> str:
    return (
        font("AI COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("DM: Chat with AZAI directly") + "\n"
        + font("Group: Mention AZAI or reply to AZAI") + "\n"
        + "/aistatus - " + font("Check AI key status") + "\n"
        + "/toneguard - " + font("Check tone guard") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def owner_text() -> str:
    return (
        font("OWNER COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/owner - " + font("Open owner panel") + "\n"
        + "/logstatus - " + font("Check log guard") + "\n"
        + font("More owner action buttons pending after live test.") + "\n\n"
        + font("Powered By:") + " " + brand()
    )


def azai_buttons():
    return [
        [Button.inline(font("Help & Cmds"), b"azai_help_cmds_menu"), Button.inline(font("System Stats"), b"azai_system_stats")],
        [Button.url(font("Add AZAI To Your Empire"), add_to_group_link())],
        [Button.url(font("Updates"), UPDATES_LINK), Button.url(font("Support"), SUPPORT_LINK)],
        [Button.url(font("My Master"), MASTER_LINK), Button.inline(font("Close"), b"azai_close_panel")],
    ]


def help_cmds_buttons():
    return [
        [Button.inline(font("Core"), b"azai_sec_core"), Button.inline(font("Profile"), b"azai_sec_profile")],
        [Button.inline(font("Verify"), b"azai_sec_verify"), Button.inline(font("Moderation"), b"azai_sec_mod")],
        [Button.inline(font("Economy"), b"azai_sec_economy"), Button.inline(font("Market"), b"azai_sec_market")],
        [Button.inline(font("Social"), b"azai_sec_social"), Button.inline(font("AI"), b"azai_sec_ai")],
        [Button.inline(font("Owner"), b"azai_sec_owner")],
        [Button.inline(font("Back"), b"azai_back_home"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


def section_buttons():
    return [[Button.inline(font("Back To Help"), b"azai_help_cmds_menu")], [Button.inline(font("Home"), b"azai_back_home"), Button.inline(font("Close"), b"azai_close_panel")]]


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
    await event.reply(azai_help_cmds_text(), file=AZAI_PANEL_MEDIA, buttons=help_cmds_buttons())


async def azai_help_cmds_menu(event):
    await event.answer(font("Opening help and commands..."))
    await event.edit(azai_help_cmds_text(), buttons=help_cmds_buttons(), file=AZAI_PANEL_MEDIA)


async def azai_commands_menu(event):
    await azai_help_cmds_menu(event)


async def azai_section_callback(event):
    data = event.data.decode()
    pages = {
        "azai_sec_core": core_text,
        "azai_sec_profile": profile_text,
        "azai_sec_verify": verify_text,
        "azai_sec_mod": mod_text,
        "azai_sec_economy": economy_text,
        "azai_sec_market": market_text,
        "azai_sec_social": social_text,
        "azai_sec_ai": ai_text,
        "azai_sec_owner": owner_text,
    }
    if data in pages:
        await event.answer()
        await event.edit(pages[data](), buttons=section_buttons())


async def azai_system_stats(event):
    await event.answer(font("Loading AZAI system stats..."))
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime = readable_time(time.time() - START_TIME)
    ist_time = datetime.now(IST).strftime("%d %b %Y - %I:%M:%S %p")
    text = (
        font("AZAI SYSTEM STATS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Brand:") + " " + brand() + "\n\n"
        + font("Performance:") + "\n"
        + font("CPU:") + f" {cpu:.1f}%\n"
        + font("RAM:") + f" {memory.percent:.1f}%\n"
        + font("Storage:") + f" {disk.percent:.1f}%\n\n"
        + font("Runtime:") + "\n"
        + font("Uptime:") + f" {uptime}\n"
        + font("Time:") + f" {ist_time}"
    )
    buttons = [
        [Button.inline(font("Back"), b"azai_back_home"), Button.inline(font("Refresh"), b"azai_system_stats")],
        [Button.inline(font("Close"), b"azai_close_panel")],
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
    tbot.add_event_handler(azai_help_cmds_menu, events.CallbackQuery(pattern=b"azai_help_cmds_menu"))
    tbot.add_event_handler(azai_commands_menu, events.CallbackQuery(pattern=b"azai_commands_menu"))
    tbot.add_event_handler(azai_section_callback, events.CallbackQuery(pattern=b"^azai_sec_"))
    tbot.add_event_handler(azai_system_stats, events.CallbackQuery(pattern=b"azai_system_stats"))
    tbot.add_event_handler(azai_back_home, events.CallbackQuery(pattern=b"azai_back_home"))
    tbot.add_event_handler(azai_close_panel, events.CallbackQuery(pattern=b"azai_close_panel"))
    tbot.handlers_loaded.add("azai_panel")
