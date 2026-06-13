from telethon import Button, events

from AloneX import font, tbot


def games_text():
    return (
        font("GAMES COMMANDS")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/dice\n/dart\n/basketball\n/slot\n\n"
        + font("Open premium economy game from below.")
    )


def games_buttons():
    return [
        [Button.inline(font("EGO HUSTLE"), b"azai_help_ego_hustle")],
        [Button.inline(font("Help Menu"), b"azai_help_cmds_menu"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


def ego_hustle_text():
    return (
        font("EGO HUSTLE COMMANDS")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Open panel:") + " /hustle /game /egohustle\n\n"
        + "/bal\n/daily\n/work\n/attack\n/raid\n/protect\n/luck\n/heist\n/leaderboard\n/top\n/profile\n\n"
        + font("One EC wallet works across AZAI economy, quiz, festival rewards, market, and EGO Hustle.")
    )


def back_buttons():
    return [[Button.inline(font("Games"), b"azai_help_games"), Button.inline(font("Close"), b"azai_close_panel")]]


async def help_games_cb(event):
    data = event.data.decode()
    if data == "azai_help_games":
        await event.edit(games_text(), buttons=games_buttons())
    elif data == "azai_help_ego_hustle":
        await event.edit(ego_hustle_text(), buttons=back_buttons())
    raise events.StopPropagation


if "aa0_azai_ego_hustle_help" not in tbot.handlers_loaded:
    tbot.add_event_handler(help_games_cb, events.CallbackQuery(pattern=b"^azai_help_(games|ego_hustle)$"))
    tbot.handlers_loaded.add("aa0_azai_ego_hustle_help")
