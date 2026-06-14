from telethon import Button

from AloneX import font
from AloneX.plugins import aaa_azai_start_pic as p


def help_buttons():
    return [
        [Button.inline(font("Core"), b"azai_help_core"), Button.inline(font("Owner"), b"azai_help_owner")],
        [Button.inline(font("Economy"), b"azai_help_economy"), Button.inline(font("Games"), b"azai_help_games")],
        [Button.inline(font("Family"), b"azai_help_family"), Button.inline(font("System"), b"azai_system_stats")],
        [Button.inline(font("Back"), b"azai_start_home"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


p.help_buttons = help_buttons
