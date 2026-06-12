from telethon import Button, events

from AloneX import font, tbot
from AloneX.plugins import aaa_azai_start_pic as p


def hb():
    return [
        [Button.inline(font("Core"), b"azai_help_core"), Button.inline(font("Owner"), b"azai_help_owner")],
        [Button.inline(font("Economy"), b"azai_help_economy"), Button.inline(font("Market"), b"azai_help_market")],
        [Button.inline(font("Family"), b"azai_help_family"), Button.inline(font("Games"), b"azai_help_games")],
        [Button.inline(font("Quiz"), b"azai_help_quiz"), Button.inline(font("Media"), b"azai_help_media")],
        [Button.inline(font("System"), b"azai_system_stats"), Button.inline(font("Back"), b"azai_start_home")],
        [Button.inline(font("Close"), b"azai_close_panel")],
    ]


def ht():
    return font("AZAI HELP & COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Choose a panel below.")


def qt():
    return font("QUIZ COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + "/animeguess\n/quiz\n/quizstats\n/quiztop"


p.help_buttons = hb
p.help_text = ht


async def cb(event):
    await event.edit(qt(), buttons=p.close_back_buttons())
    raise events.StopPropagation


if "aa_azai_help_quiz_patch" not in tbot.handlers_loaded:
    tbot.add_event_handler(cb, events.CallbackQuery(pattern=b"^azai_help_quiz$"))
    tbot.handlers_loaded.add("aa_azai_help_quiz_patch")
