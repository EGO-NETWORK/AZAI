from telethon import Button, events

from AloneX import font, prefix_cmds, tbot


def brand():
    return font("EGO Network - EST. 2026")


def help_text():
    return (
        font("AZAI HELP AND COMMANDS")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a category below to see commands and usage.")
        + "\n"
        + font("Owner-only commands stay hidden from public users.")
        + "\n\n"
        + font("Available: Core, Profile, Verify, Moderation, Economy, Market, Games, Family, AI, Owner.")
        + "\n\n"
        + font("Powered By:")
        + " "
        + brand()
    )


def help_buttons():
    return [
        [Button.inline(font("Core"), b"azai_sec_core"), Button.inline(font("Profile"), b"azai_sec_profile")],
        [Button.inline(font("Verify"), b"azai_sec_verify"), Button.inline(font("Moderation"), b"azai_sec_mod")],
        [Button.inline(font("Economy"), b"azai_sec_economy"), Button.inline(font("Market"), b"azai_sec_market")],
        [Button.inline(font("Games"), b"azai_sec_games"), Button.inline(font("Family"), b"azai_sec_family")],
        [Button.inline(font("AI"), b"azai_sec_ai"), Button.inline(font("Owner"), b"azai_sec_owner")],
        [Button.inline(font("Home"), b"azai_back_home"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


def games_text():
    return (
        font("GAMES COMMANDS")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Anime Quiz:")
        + "\n/animeguess - "
        + font("Start anime character image quiz")
        + "\n\n"
        + font("Rewards:")
        + "\n+100 EC and +15 XP for correct answer"
        + "\n5 streak bonus: +200 EC"
        + "\nDaily quiz limit: 10"
        + "\n\n"
        + font("More games will be added after live testing.")
        + "\n\n"
        + font("Powered By:")
        + " "
        + brand()
    )


def games_buttons():
    return [
        [Button.inline(font("Anime Quiz"), b"azai_games_anime")],
        [Button.inline(font("Back To Help"), b"azai_help_cmds_menu")],
        [Button.inline(font("Home"), b"azai_back_home"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


def anime_text():
    return (
        font("ANIME QUIZ")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/animeguess - "
        + font("Start a quiz with anime character image and 4 options.")
        + "\n\n"
        + font("Rules:")
        + "\n• One attempt per question"
        + "\n• Correct answer gives EC + XP"
        + "\n• Streak bonus available"
        + "\n• Owner can manage quiz from owner panel"
        + "\n\n"
        + font("Powered By:")
        + " "
        + brand()
    )


def anime_buttons():
    return [
        [Button.inline(font("Start Anime Quiz"), b"azai_quiz_start_hint")],
        [Button.inline(font("Back To Games"), b"azai_sec_games")],
        [Button.inline(font("Back To Help"), b"azai_help_cmds_menu"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


async def help_command(event):
    if event.is_channel and not event.is_group:
        return
    if event.fwd_from:
        return
    await event.reply(help_text(), buttons=help_buttons())
    raise events.StopPropagation


async def help_menu_cb(event):
    await event.answer(font("Opening Help & Commands..."))
    await event.edit(help_text(), buttons=help_buttons())
    raise events.StopPropagation


async def games_cb(event):
    await event.answer(font("Opening Games..."))
    await event.edit(games_text(), buttons=games_buttons())
    raise events.StopPropagation


async def anime_cb(event):
    await event.answer(font("Opening Anime Quiz..."))
    await event.edit(anime_text(), buttons=anime_buttons())
    raise events.StopPropagation


async def quiz_start_hint(event):
    await event.answer(font("Send /animeguess in chat to start."), alert=True)
    raise events.StopPropagation


if "aaaa_azai_help_games" not in tbot.handlers_loaded:
    tbot.add_event_handler(help_command, events.NewMessage(pattern=f"^{prefix_cmds}help(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(help_menu_cb, events.CallbackQuery(pattern=b"^azai_help_cmds_menu$"))
    tbot.add_event_handler(games_cb, events.CallbackQuery(pattern=b"^azai_sec_games$"))
    tbot.add_event_handler(anime_cb, events.CallbackQuery(pattern=b"^azai_games_anime$"))
    tbot.add_event_handler(quiz_start_hint, events.CallbackQuery(pattern=b"^azai_quiz_start_hint$"))
    tbot.handlers_loaded.add("aaaa_azai_help_games")
