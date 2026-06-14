from telethon import Button

from AloneX import font
from AloneX.plugins import aaa_azai_start_pic as start_panel


def start_buttons():
    return [
        [Button.inline(font("Help & Cmds"), b"azai_help_cmds_menu"), Button.inline(font("System Stats"), b"azai_system_stats")],
        [Button.url(font("Add AZAI To Your Empire"), start_panel.add_to_group_link())],
        [Button.url(font("Updates"), start_panel.UPDATES_LINK), Button.url(font("Support"), start_panel.SUPPORT_LINK)],
        [Button.url(font("Privacy"), start_panel.PRIVACY_LINK)],
        [Button.url(font("My Master"), start_panel.MASTER_LINK), Button.inline(font("Close"), b"azai_close_panel")],
    ]


start_panel.start_buttons = start_buttons
