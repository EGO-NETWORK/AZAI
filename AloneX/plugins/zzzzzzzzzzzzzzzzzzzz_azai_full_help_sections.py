import re

from telethon import Button, events

from AloneX import font, prefix_cmds, tbot


def _f(text: str) -> str:
    try:
        return font(text)
    except Exception:
        return text


def _menu_text() -> str:
    return (
        _f("AZAI COMMAND CENTER") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + _f("Choose a section below.") + "\n"
        + _f("Garage, gifts, social actions, market, games and owner tools are separated cleanly.")
    )


def _section(title: str, lines: list[str]) -> str:
    text = _f(title) + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for line in lines:
        text += "• " + line + "\n"
    return text


def _main_buttons():
    return [
        [Button.inline(_f("Core"), b"azai_full_core"), Button.inline(_f("Owner"), b"azai_full_owner")],
        [Button.inline(_f("Economy"), b"azai_full_economy"), Button.inline(_f("Market"), b"azai_full_market")],
        [Button.inline(_f("Garage"), b"azai_full_garage"), Button.inline(_f("Gift / Social"), b"azai_full_social")],
        [Button.inline(_f("Games"), b"azai_full_games"), Button.inline(_f("Family"), b"azai_full_family")],
        [Button.inline(_f("Media"), b"azai_full_media"), Button.inline(_f("System"), b"azai_full_system")],
        [Button.inline(_f("Close"), b"azai_full_close")],
    ]


def _back_buttons():
    return [[Button.inline(_f("Back"), b"azai_help_cmds_menu"), Button.inline(_f("Close"), b"azai_full_close")]]


SECTIONS = {
    "azai_full_core": _section("CORE COMMANDS", [
        "/start - Open AZAI home panel",
        "/help or /commands - Open command center",
        "/ping - Check bot speed/status",
        "/id - Check user/chat ID when available",
        "/profile - Open profile card when available",
    ]),
    "azai_full_owner": _section("OWNER COMMANDS", [
        "/owner - Open MR EGO owner control panel",
        "/settings - Open group settings panel",
        "/msettings - Open media settings panel",
        "/broadcast - Send official broadcast",
        "/logstatus - Check logger status",
        "/logon or /logoff - Control private logger",
        "/addfestival, /delfestival, /festivals - Festival system",
    ]),
    "azai_full_economy": _section("EGO HUSTLE / ECONOMY", [
        "/hustle - Open EGO HUSTLE home",
        "/wallet or /bal - Check EC balance",
        "/daily - Claim daily reward",
        "/work - Complete work and earn EC",
        "/luck - Try luck reward",
        "/protect - Buy protection shield",
        "/raid - Raid another user when enabled",
        "/attack - Attack another user when enabled",
        "/heist - High-risk EC heist when enabled",
        "/leaderboard or /top - Check top players",
    ]),
    "azai_full_market": _section("MARKET / SHOP", [
        "/shop or /market - Open item shop",
        "/inventory or /inv - Check owned items",
        "/gift item_id - Gift an item by replying to a user",
        "/setitempic - Owner: set item/shop media when available",
        "/setleaderpic - Owner: set leaderboard media when available",
    ]),
    "azai_full_garage": _section("GARAGE", [
        "/garage - Open garage panel",
        "/mygarage - View your garage when available",
        "/ride - Show selected ride when available",
        "/dukey - AZAI bike identity / Duke garage feature when available",
        "Use garage section for bikes, ride identity, and premium vehicle-style items.",
    ]),
    "azai_full_social": _section("GIFT / SOCIAL ACTIONS", [
        "/gift item_id - Gift item to replied user",
        "/huggy - Cute hug action",
        "/hug - Hug a replied user",
        "/pat - Pat a replied user",
        "/kiss - Kiss action when available",
        "/slap - Slap action when available",
        "/soja - Fun/social action when available",
    ]),
    "azai_full_games": _section("GAMES / QUIZ", [
        "/games - Open games panel",
        "/dice - Dice game",
        "/dart - Dart game",
        "/basketball - Basketball game",
        "/slot - Slot game",
        "/animeguess or /quiz - Anime quiz",
        "/quizlist - List quiz questions",
        "/quizauto - Owner: auto quiz control",
    ]),
    "azai_full_family": _section("FAMILY SYSTEM", [
        "/brother, /sister - Add family relation",
        "/wife, /hubby - Add clean family relation",
        "/parent, /child, /cousin - Add family relation",
        "/family - Show family list",
        "/familytree - Show family tree",
        "/removefamily - Remove relation",
        "/leavefamily - Leave family relation",
    ]),
    "azai_full_media": _section("MEDIA / CARDS", [
        "/setstartpic - Owner: set start panel media when available",
        "/setvideo - Owner: set video media when available",
        "/setsticker - Owner: set sticker media when available",
        "/setprofilepic - Owner: set profile card media when available",
        "/setleaderpic - Owner: set leaderboard card media when available",
        "/msettings - Open media settings panel",
    ]),
    "azai_full_system": _section("SYSTEM / MODERATION", [
        "/verify - Group verification command",
        "/verifyall or /unverifyall - Owner/admin verification tools",
        "/tagall - Tag all members when enabled",
        "/warn, /mute, /ban - Moderation tools when available",
        "/privacy - Privacy/legal info when available",
        "/ping - System health check",
    ]),
}


async def _send_menu(event):
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(_menu_text(), buttons=_main_buttons())
    else:
        await event.reply(_menu_text(), buttons=_main_buttons())


async def _cmd_menu(event):
    await _send_menu(event)


async def _callback(event):
    data = event.data.decode(errors="ignore")
    if data == "azai_help_cmds_menu":
        await _send_menu(event)
        raise events.StopPropagation
    if data == "azai_full_close":
        await event.delete()
        raise events.StopPropagation
    if data in SECTIONS:
        await event.edit(SECTIONS[data], buttons=_back_buttons())
        raise events.StopPropagation


_prefix_re = "[" + re.escape("".join(prefix_cmds)) + "]"
_cmd_re = rf"^{_prefix_re}(help|commands|cmds)(?:@\\w+)?$"

tbot.add_event_handler(_cmd_menu, events.NewMessage(pattern=_cmd_re, incoming=True))
tbot.add_event_handler(_callback, events.CallbackQuery(pattern=b"^(azai_help_cmds_menu|azai_full_.*)$"))
