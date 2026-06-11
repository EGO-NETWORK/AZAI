from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

BRAND = font("EGO Network - EST. 2026")


def settings_text() -> str:
    return (
        font("AZAI GROUP SETTINGS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Use these AZAI controls:") + "\n\n"
        + "/group - " + font("group panel") + "\n"
        + "/verify - " + font("verify yourself") + "\n"
        + "/verifyall - " + font("admin verify all") + "\n"
        + "/unverifyall - " + font("admin reset verification") + "\n"
        + "/mod - " + font("moderation panel") + "\n"
        + "/antilink on/off - " + font("link guard") + "\n"
        + "/commands - " + font("all commands") + "\n"
        + "/owner - " + font("owner control panel") + "\n\n"
        + font("Old settings links are redirected to AZAI branding.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def settings_buttons():
    return [
        [Button.inline(font("Verification Status"), b"azg_status")],
        [Button.inline(font("Commands"), b"azcmd_home"), Button.inline(font("Owner"), b"azop_home")],
        [Button.inline(font("Close"), b"azset_close")],
    ]


async def settings_handler(event):
    await event.reply(settings_text(), buttons=settings_buttons())
    raise events.StopPropagation


async def settings_start_handler(event):
    raw = event.raw_text or ""
    if "settings_main" not in raw.lower():
        return
    await event.reply(settings_text(), buttons=settings_buttons())
    raise events.StopPropagation


async def settings_callback(event):
    if event.data == b"azset_close":
        await event.delete()
        raise events.StopPropagation


if "aaaa_azai_settings_override" not in tbot.handlers_loaded:
    tbot.add_event_handler(settings_handler, events.NewMessage(pattern=f"^{prefix_cmds}settings(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(settings_handler, events.NewMessage(pattern=f"^{prefix_cmds}msettings(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(settings_start_handler, events.NewMessage(pattern=f"^{prefix_cmds}start(?:@\\w+)? .*$", incoming=True))
    tbot.add_event_handler(settings_callback, events.CallbackQuery(pattern=b"^azset_"))
    tbot.handlers_loaded.add("aaaa_azai_settings_override")
