from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

SUPPORT = "https://t.me/EGOxSUPPORT"
UPDATES = "https://t.me/EGOxUPDATES"


def settings_text():
    return (
        font("AZAI GROUP SETTINGS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Mode:") + " " + font("Public View") + "\n"
        + font("Network:") + " " + font("EGO Network - EST. 2026") + "\n\n"
        + font("Use /help for commands. Group setup is handled by admins and owner panels.")
    )


def buttons():
    return [[Button.url(font("Support"), SUPPORT), Button.url(font("Updates"), UPDATES)], [Button.inline(font("Close"), b"azpub_close")]]


async def settings(event):
    await event.reply(settings_text(), buttons=buttons())
    raise events.StopPropagation


async def close(event):
    await event.delete()
    raise events.StopPropagation


if "aaa0_azai_public_settings" not in tbot.handlers_loaded:
    tbot.add_event_handler(settings, events.NewMessage(pattern=f"^{prefix_cmds}settings(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(close, events.CallbackQuery(pattern=b"^azpub_close$"))
    tbot.handlers_loaded.add("aaa0_azai_public_settings")
