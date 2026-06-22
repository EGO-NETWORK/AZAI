import re

from telethon import Button, events

from AloneX import font, prefix_cmds, tbot


def f(text: str) -> str:
    try:
        return font(text)
    except Exception:
        return text


def main_text() -> str:
    return (
        f("AZAI COMMAND CENTER")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + f("Choose a command category below.")
        + "\n"
        + f("Garage, gifts, social actions, market and media tools are separated cleanly.")
    )


def section(title: str, lines: list[str]) -> str:
    text = f(title) + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for line in lines:
        text += "• " + line + "\n"
    return text


def main_buttons():
    return [
        [Button.inline(f("Core"), b"azai_full_core"), Button.inline(f("Owner"), b"azai_full_owner")],
        [Button.inline(f("Economy"), b"azai_full_economy"), Button.inline(f("Market"), b"azai_full_market")],
        [Button.inline(f("Garage"), b"azai_full_garage"), Button.inline(f("Gift / Social"), b"azai_full_social")],
        [Button.inline(f("Games"), b"azai_full_games"), Button.inline(f("Family"), b"azai_full_family")],
        [Button.inline(f("Media"), b"azai_full_media"), Button.inline(f("System"), b"azai_full_system")],
        [Button.inline(f("Close"), b"azai_full_close")],
    ]


def back_buttons():
    return [[Button.inline(f("Back"), b"azai_help_cmds_menu"), Button.inline(f("Close"), b"azai_full_close")]]


SECTIONS = {
    "azai_full_core": section("CORE COMMANDS", [
        "/start - Open AZAI home panel",
        "/help, /commands, /cmds - Open command center",
        "/ping - Check bot status",
        "/id - Check ID when available",
        "/profile - Open profile when available",
    ]),
    "azai_full_owner": section("OWNER COMMANDS", [
        "/owner - MR EGO owner panel",
        "/settings - Group settings panel",
        "/msettings - Media settings panel",
        "/broadcast - Official broadcast",
        "/logstatus - Logger status",
        "/logon, /logoff - Logger control",
        "/addfestival, /delfestival, /festivals - Festival tools",
    ]),
    "azai_full_economy": section("EGO HUSTLE / ECONOMY", [
        "/hustle - EGO HUSTLE panel",
        "/wallet, /bal - EC balance",
        "/daily - Daily reward",
        "/work - Earn EC",
        "/luck - Luck reward",
        "/protect - Shield/protection",
        "/raid, /attack, /heist - Action economy",
        "/leaderboard, /top - Top players",
    ]),
    "azai_full_market": section("MARKET / SHOP", [
        "/shop, /market - Open item shop",
        "/inventory, /inv - User inventory",
        "/gift item_id - Gift item by reply",
        "/setitempic - Owner item media",
        "/setleaderpic - Owner leaderboard media",
    ]),
    "azai_full_garage": section("GARAGE", [
        "/garage - Open garage panel",
        "/mygarage - View garage when available",
        "/ride - Selected ride when available",
        "/dukey - AZAI Duke/garage identity when available",
    ]),
    "azai_full_social": section("GIFT / SOCIAL ACTIONS", [
        "/gift item_id - Gift item to replied user",
        "/huggy - Huggy action",
        "/hug - Hug action",
        "/pat - Pat action",
        "/kiss - Kiss action when available",
        "/slap - Slap action when available",
        "/soja - Fun action when available",
    ]),
    "azai_full_games": section("GAMES / QUIZ", [
        "/games - Games panel",
        "/dice, /dart, /basketball, /slot - Telegram games",
        "/animeguess, /quiz - Anime quiz",
        "/quizlist - Quiz list",
        "/quizauto - Owner auto quiz control",
    ]),
    "azai_full_family": section("FAMILY SYSTEM", [
        "/brother, /sister, /wife, /hubby - Family relations",
        "/parent, /child, /cousin - Family relations",
        "/family - Family list",
        "/familytree - Family tree",
        "/removefamily, /leavefamily - Remove/leave relation",
    ]),
    "azai_full_media": section("MEDIA / CARDS", [
        "/setstartpic - Start media",
        "/setvideo - Video media",
        "/setsticker - Sticker media",
        "/setprofilepic - Profile card media",
        "/setleaderpic - Leaderboard card media",
        "/msettings - Media settings",
    ]),
    "azai_full_system": section("SYSTEM / MODERATION", [
        "/verify, /verifyall, /unverifyall - Verification",
        "/tagall - Tag members when enabled",
        "/warn, /mute, /ban - Moderation when available",
        "/privacy - Privacy/legal info when available",
        "/ping - Health check",
    ]),
}


async def send_main(event):
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(main_text(), buttons=main_buttons())
    else:
        await event.reply(main_text(), buttons=main_buttons())


async def command_handler(event):
    await send_main(event)
    raise events.StopPropagation


async def callback_handler(event):
    data = event.data.decode(errors="ignore")
    if data == "azai_help_cmds_menu":
        await send_main(event)
        raise events.StopPropagation
    if data == "azai_full_close":
        await event.delete()
        raise events.StopPropagation
    if data in SECTIONS:
        await event.edit(SECTIONS[data], buttons=back_buttons())
        raise events.StopPropagation


prefix_re = "[" + re.escape("".join(prefix_cmds)) + "]"
cmd_re = rf"^{prefix_re}(help|commands|cmds)(?:@\w+)?$"

tbot.add_event_handler(command_handler, events.NewMessage(pattern=cmd_re, incoming=True))
tbot.add_event_handler(callback_handler, events.CallbackQuery(pattern=b"^(azai_help_cmds_menu|azai_full_.*)$"))
