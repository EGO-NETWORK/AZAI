from telethon import Button

from AloneX import font
from AloneX.plugins import azai_owner_panel as p

_old_owner_buttons = p.owner_buttons


def owner_buttons():
    buttons = _old_owner_buttons()
    buttons.insert(5, [Button.inline(font("Media"), b"azown_market")])
    return buttons


p.owner_buttons = owner_buttons
