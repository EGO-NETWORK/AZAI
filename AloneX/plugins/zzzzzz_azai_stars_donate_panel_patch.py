from telethon import Button

from AloneX import font
from AloneX.plugins import aaa_azai_start_pic as start_panel

PATCH_FLAG = "zzzzzz_azai_stars_donate_panel_patch"


def donate_text() -> str:
    return (
        font("AZAI DONATE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Mode:") + " " + font("Telegram Stars only") + "\n"
        + font("Minimum:") + " 10 Stars\n\n"
        + font("Use:") + " /donate 10\n"
        + font("More star amounts can be added later from owner setup.")
    )


def donate_buttons():
    return [
        [Button.inline(font("Pay 10 Stars"), b"azai_donate_stars_10")],
        [Button.url(font("Support"), start_panel.SUPPORT_LINK), Button.inline(font("Back"), b"azai_start_home")],
    ]


start_panel.donate_text = donate_text
start_panel.donate_buttons = donate_buttons
